import csv
import re
import os

def clean_cpf_cnpj(value):
    if not value:
        return ''
    return re.sub(r'\D', '', value)

def truncate(value, length):
    if not value:
        return ''
    return str(value)[:length]

def escape_sql(value):
    if value is None:
        return 'NULL'
    # Basic escaping for SQL
    return "'" + str(value).replace("'", "''").replace('\\', '\\\\') + "'"

def main():
    # Check if files exist
    required_files = ['clientes.csv', 'contatos.csv', 'enderecos.csv']
    for f in required_files:
        if not os.path.exists(f):
            print(f"Error: {f} not found. Please run import_tiflux.py first.")
            return

    # Read data
    print("Reading CSV files...")
    
    clientes = {} # id -> dict
    with open('clientes.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            clientes[row['id']] = row

    enderecos = {} # client_id -> dict (first one wins)
    with open('enderecos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['client_id'] not in enderecos:
                enderecos[row['client_id']] = row

    contatos = {} # client_id -> list of dicts
    with open('contatos.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cid = row['client_id']
            if cid not in contatos:
                contatos[cid] = []
            contatos[cid].append(row)

    output_file = 'insert_dados.sql'
    print(f"Generating {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("-- SQL Insert Script generated from CSV files\n")
        f.write("-- Target Tables: clientes, cliente_emails\n")
        f.write("BEGIN;\n\n")
        
        for client_id, client in clientes.items():
            # Prepare Client Data
            nome = truncate(client.get('name', ''), 100)
            cpf_cnpj = truncate(clean_cpf_cnpj(client.get('social_revenue', '')), 20)
            
            # Address
            addr = enderecos.get(client_id, {})
            endereco = truncate(addr.get('street', ''), 100)
            numero = truncate(addr.get('number', ''), 10)
            complemento = truncate(addr.get('complement', ''), 100)
            bairro = truncate(addr.get('neighborhood', ''), 100)
            cep = truncate(addr.get('cep', ''), 20)
            cidade = truncate(addr.get('city', ''), 50)
            uf = truncate(addr.get('state', ''), 2)
            
            # Contacts
            client_contacts = contatos.get(client_id, [])
            
            # Main contact info for client table (take first contact)
            main_email = ''
            main_fone = ''
            main_celular = ''
            
            if client_contacts:
                first = client_contacts[0]
                main_email = truncate(first.get('email', ''), 255)
                main_fone = truncate(first.get('telephone', ''), 50)
                # Assuming telephone can be celular too.
            
            # Insert Client
            # Using @last_id to capture the auto-incremented ID for relationships
            # Structure: nome, email, fone, celular, cpf_cnpj, endereco, numero, complemento, bairro, cep, cidade, uf, ativo, created_at
            sql_client = f"""INSERT INTO clientes (nome, email, fone, celular, cpf_cnpj, endereco, numero, complemento, bairro, cep, cidade, uf, ativo, created_at) VALUES ({escape_sql(nome)}, {escape_sql(main_email)}, {escape_sql(main_fone)}, {escape_sql(main_celular)}, {escape_sql(cpf_cnpj)}, {escape_sql(endereco)}, {escape_sql(numero)}, {escape_sql(complemento)}, {escape_sql(bairro)}, {escape_sql(cep)}, {escape_sql(cidade)}, {escape_sql(uf)}, 'S', NOW());
SET @last_id = LAST_INSERT_ID();
"""
            f.write(sql_client)
            
            # Insert Contacts into cliente_emails
            # Structure: idcliente, email, nome, telefone, created_at, admin
            for contact in client_contacts:
                c_email = truncate(contact.get('email', ''), 255)
                c_nome = truncate(contact.get('name', ''), 50)
                c_fone = truncate(contact.get('telephone', ''), 20)
                
                # Skip if email is empty? The prompt says "para cada email deve ir um contato". 
                # If email is missing, maybe we shouldn't insert? 
                # But let's insert anyway to preserve the contact info unless it's completely empty.
                
                sql_email = f"""INSERT INTO cliente_emails (idcliente, email, nome, telefone, created_at, admin) VALUES (@last_id, {escape_sql(c_email)}, {escape_sql(c_nome)}, {escape_sql(c_fone)}, NOW(), 'N');
"""
                f.write(sql_email)
            
            f.write("\n")
        
        f.write("COMMIT;\n")

    print(f"Done. SQL script saved to {output_file}")

if __name__ == "__main__":
    main()
