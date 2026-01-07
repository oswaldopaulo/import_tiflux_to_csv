import requests
import csv
import time
import os
import sys

# Configuration
API_URL = "https://api.tiflux.com/api/v2"
RATE_LIMIT_DELAY = 0.4  # 3 requests per second -> ~0.33s. Using 0.4s to be safe.

# File paths
CLIENTES_CSV = "clientes.csv"
CONTATOS_CSV = "contatos.csv"
ENDERECOS_CSV = "enderecos.csv"
SOLICITANTES_CSV = "solicitantes.csv"

# Global headers variable, will be initialized in main
HEADERS = {}

def make_request(url, params=None):
    """Helper to make requests with rate limiting."""
    try:
        response = requests.get(url, headers=HEADERS, params=params)
        time.sleep(RATE_LIMIT_DELAY)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error {response.status_code} fetching {url}: {response.text}")
            return None
    except Exception as e:
        print(f"Exception fetching {url}: {e}")
        return None

def save_to_csv(file_obj, writer, data, headers_written, fieldnames_ref):
    """Helper to save data to CSV, handling headers."""
    if not data:
        return

    # Flatten data if necessary or just use keys
    # Assuming data is a flat dictionary for CSV
    
    if not headers_written[0]:
        fieldnames = list(data.keys())
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        headers_written[0] = True
        fieldnames_ref[0] = fieldnames
        # Re-create writer with fixed fieldnames for subsequent writes
        return writer
    
    # If writer exists, use it
    if writer:
        writer.writerow(data)
    return writer

def main():
    global HEADERS
    
    print("Please enter your Tiflux Bearer Token:")
    token = input().strip()
    if not token:
        print("Token cannot be empty.")
        sys.exit(1)
        
    HEADERS = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "multipart/form-data"
    }

    # Open files
    files = {}
    writers = {}
    headers_written = {} # Key: file_type, Value: [bool]
    fieldnames_refs = {} # Key: file_type, Value: [list]

    file_configs = {
        'clientes': CLIENTES_CSV,
        'contatos': CONTATOS_CSV,
        'enderecos': ENDERECOS_CSV,
        'solicitantes': SOLICITANTES_CSV
    }

    for key, path in file_configs.items():
        f = open(path, mode='w', newline='', encoding='utf-8')
        files[key] = f
        writers[key] = None
        headers_written[key] = [False]
        fieldnames_refs[key] = [None]

    try:
        offset = 1
        limit = 30 # Page size
        
        while True:
            print(f"Fetching clients page {offset}...")
            clients_list = make_request(f"{API_URL}/clients", params={"offset": offset, "limit": limit})
            
            if not clients_list:
                print("No more clients or error.")
                break
            
            # If the API returns a list directly
            if isinstance(clients_list, list):
                current_batch = clients_list
            elif isinstance(clients_list, dict) and 'data' in clients_list:
                 current_batch = clients_list['data']
            else:
                # Fallback if structure is unknown, assuming list
                current_batch = clients_list

            if not current_batch:
                print("Empty batch, finishing.")
                break

            for client_summary in current_batch:
                client_id = client_summary.get('id')
                if not client_id:
                    continue

                print(f"Processing client {client_id}...")

                # 1. Get Client Details
                client_details = make_request(f"{API_URL}/clients/{client_id}")
                if client_details:
                    # Initialize writer if needed
                    if not writers['clientes']:
                        writers['clientes'] = save_to_csv(files['clientes'], None, client_details, headers_written['clientes'], fieldnames_refs['clientes'])
                        # Write the first row immediately after creating writer
                        writers['clientes'].writerow(client_details)
                    else:
                        writers['clientes'].writerow(client_details)

                    # 2. Get Contacts
                    contact_ids = client_details.get('contact_ids', [])
                    for cid in contact_ids:
                        contact_data = make_request(f"{API_URL}/clients/{client_id}/contacts/{cid}")
                        if contact_data:
                            contact_data['client_id'] = client_id # Add FK
                            if not writers['contatos']:
                                writers['contatos'] = save_to_csv(files['contatos'], None, contact_data, headers_written['contatos'], fieldnames_refs['contatos'])
                                writers['contatos'].writerow(contact_data)
                            else:
                                writers['contatos'].writerow(contact_data)

                    # 3. Get Addresses
                    address_ids = client_details.get('address_ids', [])
                    for aid in address_ids:
                        address_data = make_request(f"{API_URL}/clients/{client_id}/addresses/{aid}")
                        if address_data:
                            address_data['client_id'] = client_id # Add FK
                            if not writers['enderecos']:
                                writers['enderecos'] = save_to_csv(files['enderecos'], None, address_data, headers_written['enderecos'], fieldnames_refs['enderecos'])
                                writers['enderecos'].writerow(address_data)
                            else:
                                writers['enderecos'].writerow(address_data)

                    # 4. Get Requestors
                    # First get list
                    requestors_list = make_request(f"{API_URL}/clients/{client_id}/requestors")
                    if requestors_list:
                        # Handle if it's wrapped in 'data' or is a list
                        r_list = requestors_list if isinstance(requestors_list, list) else requestors_list.get('data', [])
                        
                        for req in r_list:
                            req_id = req.get('id')
                            if req_id:
                                requestor_data = make_request(f"{API_URL}/clients/{client_id}/requestors/{req_id}")
                                if requestor_data:
                                    requestor_data['client_id'] = client_id # Add FK
                                    if not writers['solicitantes']:
                                        writers['solicitantes'] = save_to_csv(files['solicitantes'], None, requestor_data, headers_written['solicitantes'], fieldnames_refs['solicitantes'])
                                        writers['solicitantes'].writerow(requestor_data)
                                    else:
                                        writers['solicitantes'].writerow(requestor_data)

            offset += 1

    finally:
        for f in files.values():
            f.close()
        print("Done.")

if __name__ == "__main__":
    main()
