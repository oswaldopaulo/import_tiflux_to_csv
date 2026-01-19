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

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- SQL Insert Script for Departments, Products, Types and Relations\n")
        f.write("BEGIN;\n\n")

        # 1. Departamentos (from mesas.csv)
        # Table: departamentos
        # Fields: id, descricao, icone, ativo, idtipo, portal_cliente, id_termo_personalizado, valor_departamento
        print("Processing Departamentos...")
        with open('mesas.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                d_id = row['id']
                descricao = truncate(row['name'], 100)
                ativo_val = row['active']
                ativo = 'S' if ativo_val.lower() == 'true' else 'N'
                
                # Insert with ID to preserve relationship
                sql = f"INSERT INTO departamentos (id, descricao, ativo, idtipo, portal_cliente) VALUES ({d_id}, {escape_sql(descricao)}, '{ativo}', 1, 1);\n"
                f.write(sql)
        
        f.write("\n")

        # 2. Produtos (from catalogos.csv)
        # Table: produtos
        # Fields: id, descricao, icone, ativo, idsla, portal_cliente, id_termo_personalizado, valor_categoria
        print("Processing Produtos...")
        with open('catalogos.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                p_id = row['id']
                descricao = truncate(row['name'], 100)
                
                # icone is NOT NULL in structure, using empty string
                sql = f"INSERT INTO produtos (id, descricao, icone, ativo, portal_cliente) VALUES ({p_id}, {escape_sql(descricao)}, '', 'S', 1);\n"
                f.write(sql)

        f.write("\n")

        # 3. Tipos (from itensdocatalogo.csv)
        # Table: tipos
        # Fields: id, descricao, ativo, icone, idproduto, portal_cliente, id_termo_personalizado, valor_tipo
        print("Processing Tipos...")
        with open('itensdocatalogo.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                t_id = row['id']
                name = row['name']
                area_str = row['area']
                area_dict = parse_dict_str(area_str)
                area_name = area_dict.get('name', '')
                
                full_desc = f"{name} - {area_name}" if area_name else name
                full_desc = truncate(full_desc, 100)
                
                id_produto = row['id_catalogo']
                
                # icone is NOT NULL in structure
                sql = f"INSERT INTO tipos (id, descricao, ativo, icone, idproduto, portal_cliente) VALUES ({t_id}, {escape_sql(full_desc)}, 'S', '', {id_produto}, 1);\n"
                f.write(sql)

        f.write("\n")

        # 4. Produto_Departamentos
        # Table: produto_departamentos
        # Fields: id, idproduto, iddepartamento
        # Mapping: idproduto -> catalogos.id, iddepartamento -> catalogos.id_mesa
        print("Processing Produto_Departamentos...")
        with open('catalogos.csv', 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                p_id = row['id']
                mesa_id = row['id_mesa']
                
                sql = f"INSERT INTO produto_departamentos (id, idproduto, iddepartamento) VALUES (NULL, {p_id}, {mesa_id});\n"
                f.write(sql)

        f.write("\nCOMMIT;\n")
    
    print("Done.")

if __name__ == "__main__":
    main()
