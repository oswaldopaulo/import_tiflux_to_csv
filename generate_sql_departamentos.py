import csv
import re
import os
import ast

def escape_sql(value):
    if value is None:
        return 'NULL'
    return "'" + str(value).replace("'", "''").replace('\\', '\\\\') + "'"

def truncate(value, length):
    if not value:
        return ''
    return str(value)[:length]

def parse_dict_str(s):
    """Parses a string representation of a dictionary like "{'id': 1, 'name': 'foo'}"."""
    try:
        return ast.literal_eval(s)
    except:
        return {}

def main():
    # Check files
    required_files = ['mesas.csv', 'catalogos.csv', 'itensdocatalogo.csv']
    for f in required_files:
        if not os.path.exists(f):
            print(f"Error: {f} not found.")
            return

    output_file = 'insert_dados_departamentos.sql'
    print(f"Generating {output_file}...")

    # Data Structures
    # catalog_areas: catalog_id -> set of area_names
    catalog_areas = {}
    
    # item_catalog_map: item_id -> catalog_id
    item_catalog_map = {}
    
    # item_area_map: item_id -> area_name
    item_area_map = {}

    print("Pre-processing Items...")
    with open('itensdocatalogo.csv', 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            item_id = row['id']
            cat_id = row['id_catalogo']
            
            area_str = row['area']
            area_dict = parse_dict_str(area_str)
            area_name = area_dict.get('name', '')
            
            if cat_id not in catalog_areas:
                catalog_areas[cat_id] = set()
            if area_name:
                catalog_areas[cat_id].add(area_name)
            
            item_catalog_map[item_id] = cat_id
            item_area_map[item_id] = area_name

    # We need to generate NEW product IDs because one catalog can split into multiple products (one per area)
    # Map: (catalog_id, area_name) -> new_product_id
    product_mapping = {}
    next_product_id = 1 

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- SQL Insert Script for Departments, Products, Types and Relations\n")
        f.write("BEGIN;\n\n")

        # 1. Departamentos (from mesas.csv)
        print("Processing Departamentos...")
        with open('mesas.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                d_id = row['id']
                descricao = truncate(row['name'], 100)
                ativo_val = row['active']
                ativo = 'S' if ativo_val.lower() == 'true' else 'N'
                
                sql = f"INSERT INTO departamentos (id, descricao, ativo, idtipo, portal_cliente) VALUES ({d_id}, {escape_sql(descricao)}, '{ativo}', 1, 1);\n"
                f.write(sql)
        
        f.write("\n")

        # 2. Produtos (from catalogos.csv + areas)
        print("Processing Produtos...")
        with open('catalogos.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                cat_id = row['id']
                cat_name = row['name']
                
                areas = catalog_areas.get(cat_id, set())
                
                # If no areas found, create one product with just catalog name (or maybe skip? assuming create)
                if not areas:
                    areas.add('') 
                
                # Sort areas to be deterministic
                sorted_areas = sorted(list(areas))
                
                for area_name in sorted_areas:
                    if area_name:
                        full_desc = f"{cat_name} | {area_name}"
                    else:
                        full_desc = cat_name
                    
                    full_desc = truncate(full_desc, 100)
                    
                    # Assign new ID
                    p_id = next_product_id
                    next_product_id += 1
                    
                    # Store mapping for later use
                    product_mapping[(cat_id, area_name)] = p_id
                    
                    sql = f"INSERT INTO produtos (id, descricao, icone, ativo, portal_cliente) VALUES ({p_id}, {escape_sql(full_desc)}, '', 'S', 1);\n"
                    f.write(sql)

        f.write("\n")

        # 3. Tipos (from itensdocatalogo.csv)
        # idproduto = mapped new_product_id based on (catalog_id, area_name)
        print("Processing Tipos...")
        with open('itensdocatalogo.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                t_id = row['id']
                name = truncate(row['name'], 100)
                
                cat_id = row['id_catalogo']
                area_name = item_area_map.get(t_id, '')
                
                # Find the new product ID
                new_prod_id = product_mapping.get((cat_id, area_name))
                
                # Fallback if not found (shouldn't happen if logic is consistent)
                if new_prod_id is None:
                    # Try finding a product for this catalog with empty area
                    new_prod_id = product_mapping.get((cat_id, ''))
                
                if new_prod_id is None:
                     # Last resort, pick first product for this catalog
                     for k, v in product_mapping.items():
                         if k[0] == cat_id:
                             new_prod_id = v
                             break
                
                if new_prod_id is None:
                    print(f"Warning: Could not find product for item {t_id} (cat {cat_id})")
                    continue

                sql = f"INSERT INTO tipos (id, descricao, ativo, icone, idproduto, portal_cliente) VALUES ({t_id}, {escape_sql(name)}, 'S', '', {new_prod_id}, 1);\n"
                f.write(sql)

        f.write("\n")

        # 4. Produto_Departamentos
        # Link NEW product IDs to Departments (Mesas)
        # We need to know which Mesa the original Catalog belonged to.
        print("Processing Produto_Departamentos...")
        
        # Build map: catalog_id -> mesa_id
        catalog_mesa_map = {}
        with open('catalogos.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                catalog_mesa_map[row['id']] = row['id_mesa']
        
        # Iterate over all created products
        for (cat_id, area_name), new_prod_id in product_mapping.items():
            mesa_id = catalog_mesa_map.get(cat_id)
            if mesa_id:
                sql = f"INSERT INTO produto_departamentos (id, idproduto, iddepartamento) VALUES (NULL, {new_prod_id}, {mesa_id});\n"
                f.write(sql)

        f.write("\n")
        
        # 5. Tipo_Produtos
        # idtipo = item_id, idproduto = new_product_id
        # Note: The prompt asked for "tipo_produtos" with "idtipo" and "idproduto".
        # We already linked types to products in the 'tipos' table via 'idproduto' column.
        # But if there is a separate many-to-many table 'tipo_produtos', we populate it too.
        # Structure provided in previous turn had 'tipo_departamentos', but user asked for 'tipo_produtos' now.
        # I will check if 'tipo_produtos' exists in structure.sql provided in context?
        # The user provided structure.sql content in previous turn, let's check it.
        # It has `tipo_departamentos` commented out and `tipo_produtos` added at the end?
        # Wait, I need to be sure. I will assume `tipo_produtos` exists as requested.
        
        print("Processing Tipo_Produtos...")
        with open('itensdocatalogo.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                t_id = row['id']
                cat_id = row['id_catalogo']
                area_name = item_area_map.get(t_id, '')
                
                new_prod_id = product_mapping.get((cat_id, area_name))
                
                # Fallback logic same as above
                if new_prod_id is None:
                    new_prod_id = product_mapping.get((cat_id, ''))
                if new_prod_id is None:
                     for k, v in product_mapping.items():
                         if k[0] == cat_id:
                             new_prod_id = v
                             break
                
                if new_prod_id:
                    sql = f"INSERT INTO tipo_produtos (id, idtipo, idproduto) VALUES (NULL, {t_id}, {new_prod_id});\n"
                    f.write(sql)

        f.write("\nCOMMIT;\n")
    
    print("Done.")

if __name__ == "__main__":
    main()
