import pandas as pd
import os
import ast
import json

def escape_sql_string(val):
    if pd.isna(val):
        return "NULL"
    # Escape single quotes
    return "'" + str(val).replace("'", "''") + "'"

def get_col_value(row, col_names, default=None):
    """Try to get value from multiple potential column names."""
    for col in col_names:
        if col in row:
            return row[col]
    return default

def map_ativo(val):
    """Map boolean/integer active status to 'S'/'N'."""
    if pd.isna(val):
        return "'S'" # Default to Active if unknown
    
    s_val = str(val).lower()
    if s_val in ['1', 'true', 's', 'sim', 'yes']:
        return "'S'"
    return "'N'"

def truncate_string(val, length):
    if val is None:
        return ""
    s_val = str(val)
    if len(s_val) > length:
        return s_val[:length]
    return s_val

def parse_area_name(area_val):
    """Parses the area column which might be a string representation of a dict."""
    if pd.isna(area_val) or str(area_val).strip() == '':
        return ''
    
    s_area = str(area_val).strip()
    
    # If it doesn't look like a dict, return as is
    if not s_area.startswith('{'):
        return s_area

    # Try parsing as Python literal (most likely for CSV written by Python)
    try:
        data = ast.literal_eval(s_area)
        if isinstance(data, dict):
            return str(data.get('name', ''))
    except:
        pass

    # Try parsing as JSON (if double quotes were used)
    try:
        data = json.loads(s_area)
        if isinstance(data, dict):
            return str(data.get('name', ''))
    except:
        pass
        
    return ''

def generate_sql():
    # Load CSV files
    try:
        # Using dtype=str to preserve IDs and prevent float conversion of nullable ints
        # Trying 'mesas.csv' first as it is the output of import_catalogo.py
        mesas_df = pd.read_csv('mesas.csv', dtype=str)
        catalogos_df = pd.read_csv('catalogos.csv', dtype=str)
        itens_df = pd.read_csv('itensdocatalogo.csv', dtype=str)
    except FileNotFoundError:
        # Fallback for mesa.csv vs mesas.csv
        try:
            mesas_df = pd.read_csv('mesa.csv', dtype=str)
            catalogos_df = pd.read_csv('catalogos.csv', dtype=str)
            itens_df = pd.read_csv('itensdocatalogo.csv', dtype=str)
        except FileNotFoundError as e:
            print(f"Error loading CSV files: {e}")
            return

    sql_statements = []
    
    # ---------------------------------------------------------
    # 1. Tabela departamentos
    # ---------------------------------------------------------
    # Structure: id, descricao, icone, ativo, idtipo, portal_cliente, id_termo_personalizado, valor_departamento
    print("Generating SQL for departamentos...")
    for _, row in mesas_df.iterrows():
        id_val = row.get('id')
        if pd.isna(id_val): continue
        
        # Descricao
        desc_raw = get_col_value(row, ['descricao', 'name', 'description'], '')
        desc_trunc = truncate_string(desc_raw, 100)
        descricao = escape_sql_string(desc_trunc)
        
        # Ativo
        ativo_raw = get_col_value(row, ['ativo', 'active', 'enabled'], '1')
        ativo = map_ativo(ativo_raw)
        
        sql = f"INSERT INTO departamentos (id, descricao, icone, ativo, idtipo, portal_cliente, id_termo_personalizado, valor_departamento) VALUES ({id_val}, {descricao}, NULL, {ativo}, 1, 1, NULL, NULL);"
        sql_statements.append(sql)

    # ---------------------------------------------------------
    # 2. Tabela produtos
    # ---------------------------------------------------------
    # Structure: id, descricao, icone, ativo, idsla, portal_cliente, id_termo_personalizado, valor_categoria
    print("Generating SQL for produtos...")
    for _, row in catalogos_df.iterrows():
        id_val = row.get('id')
        if pd.isna(id_val): continue

        # Descricao
        desc_raw = get_col_value(row, ['descricao', 'name', 'description'], '')
        desc_trunc = truncate_string(desc_raw, 100)
        descricao = escape_sql_string(desc_trunc)
        
        sql = f"INSERT INTO produtos (id, descricao, icone, ativo, idsla, portal_cliente, id_termo_personalizado, valor_categoria) VALUES ({id_val}, {descricao}, '', 'S', NULL, 1, NULL, NULL);"
        sql_statements.append(sql)

    # ---------------------------------------------------------
    # 3. Tabela tipos
    # ---------------------------------------------------------
    # Structure: id, descricao, ativo, icone, idproduto, portal_cliente, id_termo_personalizado, valor_tipo
    print("Generating SQL for tipos...")
    for _, row in itens_df.iterrows():
        id_val = row.get('id')
        if pd.isna(id_val): continue

        # Descricao: name + " - " + area.name
        name = get_col_value(row, ['name', 'descricao'], '')
        area_raw = get_col_value(row, ['area'], '')
        area_name = parse_area_name(area_raw)
        
        if area_name:
            desc_combined = f"{name} - {area_name}".strip()
        else:
            desc_combined = name.strip()
            
        desc_trunc = truncate_string(desc_combined, 100)
        descricao = escape_sql_string(desc_trunc)
        
        # idproduto -> id_catalogo
        idproduto = row.get('id_catalogo')
        if pd.isna(idproduto): idproduto = "NULL"
        
        sql = f"INSERT INTO tipos (id, descricao, ativo, icone, idproduto, portal_cliente, id_termo_personalizado, valor_tipo) VALUES ({id_val}, {descricao}, 'S', '', {idproduto}, 1, NULL, NULL);"
        sql_statements.append(sql)

    # ---------------------------------------------------------
    # 4. Tabela produto_departamentos
    # ---------------------------------------------------------
    # Structure: id (auto), idproduto, iddepartamento
    # Link: catalogos.csv (id=idproduto, id_mesa=iddepartamento)
    print("Generating SQL for produto_departamentos...")
    for _, row in catalogos_df.iterrows():
        idproduto = row.get('id')
        iddepartamento = row.get('id_mesa')
        
        if pd.notna(idproduto) and pd.notna(iddepartamento):
            sql = f"INSERT INTO produto_departamentos (idproduto, iddepartamento) VALUES ({idproduto}, {iddepartamento});"
            sql_statements.append(sql)

    # ---------------------------------------------------------
    # 5. Tabela tipo_produtos
    # ---------------------------------------------------------
    # Structure: id (auto), idtipo, idproduto
    # Link: itensdocatalogo.csv (id=idtipo, id_catalogo=idproduto)
    print("Generating SQL for tipo_produtos...")
    for _, row in itens_df.iterrows():
        idtipo = row.get('id')
        idproduto = row.get('id_catalogo')
        
        if pd.notna(idtipo) and pd.notna(idproduto):
            sql = f"INSERT INTO tipo_produtos (idtipo, idproduto) VALUES ({idtipo}, {idproduto});"
            sql_statements.append(sql)

    # Write to file
    output_file = 'insert_dados_departamentos.sql'
    with open(output_file, 'w', encoding='utf-8') as f:
        for statement in sql_statements:
            f.write(statement + '\n')
            
    print(f"SQL generation complete. Output in {output_file}")

if __name__ == "__main__":
    generate_sql()
