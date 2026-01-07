import csv
import sys
import os

def read_csv_as_dict(filename, key_field):
    """Reads a CSV file into a dictionary keyed by key_field.
       Handles multiple entries for the same key by keeping the first one found.
    """
    data = {}
    if not os.path.exists(filename):
        print(f"Warning: {filename} not found.")
        return data
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = row.get(key_field)
                if key and key not in data:
                    data[key] = row
    except Exception as e:
        print(f"Error reading {filename}: {e}")
    return data

def main():
    # 1. Read source files
    # Clientes keyed by 'id'
    clientes = read_csv_as_dict('clientes.csv', 'id')
    
    # Contatos keyed by 'client_id' (first one wins)
    contatos = read_csv_as_dict('contatos.csv', 'client_id')
    
    # Enderecos keyed by 'client_id' (first one wins)
    enderecos = read_csv_as_dict('enderecos.csv', 'client_id')
    
    # 2. Prepare output
    output_filename = 'modelosndesk.csv'
    
    # Default fieldnames
    fieldnames = ['nome','email','fone','celular','cpf_cnpj','endereco','numero','complemento','bairro','cep','cidade','uf']
    
    # Read the header from the existing output file to preserve order if it exists
    if os.path.exists(output_filename):
        try:
            with open(output_filename, 'r', encoding='utf-8') as f:
                header_line = f.readline().strip()
                if header_line:
                    read_fields = header_line.split(';')
                    # Basic validation to see if it looks like our header
                    if 'nome' in read_fields: 
                        fieldnames = read_fields
        except:
            pass

    # 3. Merge data
    merged_rows = []
    seen_keys = set() # To track duplicates based on CPF/CNPJ
    
    for client_id, client_data in clientes.items():
        row = {}
        
        # Get related data
        contato = contatos.get(client_id, {})
        endereco = enderecos.get(client_id, {})
        
        # Map fields to modelosndesk columns
        row['nome'] = client_data.get('name', '')
        row['email'] = contato.get('email', '')
        row['fone'] = contato.get('telephone', '')
        row['celular'] = '' 
        row['cpf_cnpj'] = client_data.get('social_revenue', '')
        
        # Endereco fields
        row['endereco'] = endereco.get('street', '')
        row['numero'] = endereco.get('number', '')
        row['complemento'] = endereco.get('complement', '')
        row['bairro'] = endereco.get('neighborhood', '')
        row['cep'] = endereco.get('cep', '')
        row['cidade'] = endereco.get('city', '')
        row['uf'] = endereco.get('state', '')
        
        # Filter duplicates based on CPF/CNPJ
        cpf = row.get('cpf_cnpj')
        if cpf:
            if cpf in seen_keys:
                continue # Skip duplicate
            seen_keys.add(cpf)
        
        merged_rows.append(row)

    # 4. Write to CSV with semicolon separator
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=';')
            writer.writeheader()
            writer.writerows(merged_rows)
        print(f"Successfully merged data into {output_filename}")
    except IOError as e:
        print(f"Error writing to {output_filename}: {e}")

if __name__ == "__main__":
    main()
