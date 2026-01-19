import requests
import csv
import time
import os
import sys

# Configuration
API_URL = "https://api.tiflux.com/api/v2"
RATE_LIMIT_DELAY = 0.4  # 3 requests per second -> ~0.33s. Using 0.4s to be safe.

# File paths
MESAS_CSV = "mesas.csv"
CATALOGOS_CSV = "catalogos.csv"
ITENS_CATALOGO_CSV = "itensdocatalogo.csv"

# Global headers variable
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
        'mesas': MESAS_CSV,
        'catalogos': CATALOGOS_CSV,
        'itens': ITENS_CATALOGO_CSV
    }

    for key, path in file_configs.items():
        f = open(path, mode='w', newline='', encoding='utf-8')
        files[key] = f
        writers[key] = None
        headers_written[key] = [False]
        fieldnames_refs[key] = [None]

    try:
        # 1. Fetch Mesas (Desks)
        offset = 1
        limit = 30
        
        while True:
            print(f"Fetching desks page {offset}...")
            desks_list = make_request(f"{API_URL}/desks", params={"offset": offset, "limit": limit})
            
            if not desks_list:
                print("No more desks or error.")
                break
            
            # Handle list or dict wrapper
            if isinstance(desks_list, list):
                current_batch = desks_list
            elif isinstance(desks_list, dict) and 'data' in desks_list:
                 current_batch = desks_list['data']
            else:
                current_batch = desks_list

            if not current_batch:
                print("Empty batch of desks, finishing.")
                break

            for desk in current_batch:
                desk_id = desk.get('id')
                if not desk_id:
                    continue

                print(f"Processing desk {desk_id}...")
                
                # Save Mesa
                if not writers['mesas']:
                    writers['mesas'] = save_to_csv(files['mesas'], None, desk, headers_written['mesas'], fieldnames_refs['mesas'])
                    writers['mesas'].writerow(desk)
                else:
                    writers['mesas'].writerow(desk)

                # 2. Fetch Catalogs for this Desk
                cat_offset = 1
                cat_limit = 30
                while True:
                    print(f"  Fetching catalogs for desk {desk_id} page {cat_offset}...")
                    catalogs_list = make_request(f"{API_URL}/desks/{desk_id}/services-catalogs", params={"offset": cat_offset, "limit": cat_limit})
                    
                    if not catalogs_list:
                        break
                        
                    if isinstance(catalogs_list, list):
                        cat_batch = catalogs_list
                    elif isinstance(catalogs_list, dict) and 'data' in catalogs_list:
                        cat_batch = catalogs_list['data']
                    else:
                        cat_batch = catalogs_list
                        
                    if not cat_batch:
                        break
                        
                    for catalog in cat_batch:
                        catalog_id = catalog.get('id')
                        catalog['id_mesa'] = desk_id # Add FK
                        
                        # Save Catalog
                        if not writers['catalogos']:
                            writers['catalogos'] = save_to_csv(files['catalogos'], None, catalog, headers_written['catalogos'], fieldnames_refs['catalogos'])
                            writers['catalogos'].writerow(catalog)
                        else:
                            writers['catalogos'].writerow(catalog)
                            
                        # 3. Fetch Catalog Items
                        if catalog_id:
                            item_offset = 1
                            item_limit = 30
                            while True:
                                # print(f"    Fetching items for catalog {catalog_id} page {item_offset}...")
                                items_list = make_request(f"{API_URL}/desks/{desk_id}/services-catalogs-items", 
                                                          params={"catalog_id": catalog_id, "offset": item_offset, "limit": item_limit})
                                
                                if not items_list:
                                    break
                                    
                                if isinstance(items_list, list):
                                    item_batch = items_list
                                elif isinstance(items_list, dict) and 'data' in items_list:
                                    item_batch = items_list['data']
                                else:
                                    item_batch = items_list
                                    
                                if not item_batch:
                                    break
                                    
                                for item in item_batch:
                                    item['id_mesa'] = desk_id
                                    item['id_catalogo'] = catalog_id
                                    
                                    # Save Item
                                    if not writers['itens']:
                                        writers['itens'] = save_to_csv(files['itens'], None, item, headers_written['itens'], fieldnames_refs['itens'])
                                        writers['itens'].writerow(item)
                                    else:
                                        writers['itens'].writerow(item)
                                
                                item_offset += 1
                                # Safety break for items loop if needed, but relying on empty batch
                    
                    cat_offset += 1
            
            offset += 1

    finally:
        for f in files.values():
            f.close()
        print("Done.")

if __name__ == "__main__":
    main()
