import requests
import csv
import time
import os
import sys

# Configuration
API_URL = "https://api.tiflux.com/api/v2"
RATE_LIMIT_DELAY = 0.4  # 3 requests per second -> ~0.33s. Using 0.4s to be safe.

# File paths
TICKETS_CSV = "tickets.csv"
TICKET_FILES_CSV = "ticket_files.csv"
ANSWERS_CSV = "respostas.csv"

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
        return writer

    # Flatten data if necessary or just use keys
    
    if not headers_written[0]:
        fieldnames = list(data.keys())
        # Ensure ticket_number is in fieldnames if we added it manually and it wasn't there
        if 'ticket_number' in data and 'ticket_number' not in fieldnames:
            fieldnames.append('ticket_number')
            
        print(f"Creating CSV with columns: {fieldnames}")
        writer = csv.DictWriter(file_obj, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        headers_written[0] = True
        fieldnames_ref[0] = fieldnames
        file_obj.flush()
        return writer
    
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
        'tickets': TICKETS_CSV,
        'files': TICKET_FILES_CSV,
        'answers': ANSWERS_CSV
    }

    for key, path in file_configs.items():
        f = open(path, mode='w', newline='', encoding='utf-8')
        files[key] = f
        writers[key] = None
        headers_written[key] = [False]
        fieldnames_refs[key] = [None]

    try:
        # 1. Fetch Tickets
        offset = 104
        limit = 100 # Page size as requested in example URL (offset=100&limit=100)
        
        while True:
            print(f"Fetching tickets page {offset}...")
            # filter_by=all is required to get all tickets
            tickets_list = make_request(f"{API_URL}/tickets", params={"offset": offset, "limit": limit, "filter_by": "all"})
            
            if not tickets_list:
                print("No more tickets or error.")
                break
            
            # Handle list or dict wrapper
            if isinstance(tickets_list, list):
                current_batch = tickets_list
            elif isinstance(tickets_list, dict) and 'data' in tickets_list:
                 current_batch = tickets_list['data']
            else:
                current_batch = []

            if not current_batch:
                print("Empty batch of tickets, finishing.")
                break

            print(f"Found {len(current_batch)} tickets in this batch.")

            for ticket_summary in current_batch:
                # User specified using 'ticket_number' from the list
                # We try to get 'ticket_number', fallback to 'id' if missing but prefer ticket_number
                ticket_num = ticket_summary.get('ticket_number')
                if not ticket_num:
                    ticket_num = ticket_summary.get('id')
                
                if not ticket_num:
                    print("Skipping ticket without ticket_number or id")
                    continue

                print(f"Processing ticket {ticket_num}...")

                # 1.1 Get Detailed Ticket Data
                # Endpoint: /tickets/{ticket_number}
                ticket_details = make_request(f"{API_URL}/tickets/{ticket_num}")
                if ticket_details:
                    # Unwrap 'data' if present
                    if isinstance(ticket_details, dict) and 'data' in ticket_details and isinstance(ticket_details['data'], dict):
                        ticket_details = ticket_details['data']

                    if not writers['tickets']:
                        writers['tickets'] = save_to_csv(files['tickets'], None, ticket_details, headers_written['tickets'], fieldnames_refs['tickets'])
                        writers['tickets'].writerow(ticket_details)
                        files['tickets'].flush()
                    else:
                        writers['tickets'].writerow(ticket_details)
                        files['tickets'].flush()

                # 1.2 Get Ticket Files
                # Endpoint: /tickets/{ticket_number}/files
                files_offset = 1
                files_limit = 100
                while True:
                    files_list = make_request(f"{API_URL}/tickets/{ticket_num}/files", params={"offset": files_offset, "limit": files_limit})
                    
                    if not files_list:
                        break
                    
                    if isinstance(files_list, list):
                        f_batch = files_list
                    elif isinstance(files_list, dict) and 'data' in files_list:
                        f_batch = files_list['data']
                    else:
                        f_batch = []
                        
                    if not f_batch:
                        break
                        
                    for file_data in f_batch:
                        if isinstance(file_data, dict) and 'data' in file_data and isinstance(file_data['data'], dict):
                            file_data = file_data['data']

                        file_data['ticket_number'] = ticket_num # Add FK
                        
                        if not writers['files']:
                            writers['files'] = save_to_csv(files['files'], None, file_data, headers_written['files'], fieldnames_refs['files'])
                            writers['files'].writerow(file_data)
                            files['files'].flush()
                        else:
                            writers['files'].writerow(file_data)
                            files['files'].flush()
                    
                    files_offset += 1

                # 1.3 Get Ticket Answers
                # Endpoint: /tickets/{ticket_number}/answers
                answers_offset = 1
                answers_limit = 100
                while True:
                    answers_list = make_request(f"{API_URL}/tickets/{ticket_num}/answers", params={"offset": answers_offset, "limit": answers_limit})
                    
                    if not answers_list:
                        break
                        
                    if isinstance(answers_list, list):
                        a_batch = answers_list
                    elif isinstance(answers_list, dict) and 'data' in answers_list:
                        a_batch = answers_list['data']
                    else:
                        a_batch = []
                        
                    if not a_batch:
                        break
                        
                    for answer_summary in a_batch:
                        answer_id = answer_summary.get('id')
                        if answer_id:
                            # Fetch detailed answer
                            # Endpoint: /tickets/{ticket_number}/answers/{id}
                            answer_details = make_request(f"{API_URL}/tickets/{ticket_num}/answers/{answer_id}")
                            if answer_details:
                                if isinstance(answer_details, dict) and 'data' in answer_details and isinstance(answer_details['data'], dict):
                                    answer_details = answer_details['data']

                                answer_details['ticket_number'] = ticket_num # Add FK
                                
                                if not writers['answers']:
                                    writers['answers'] = save_to_csv(files['answers'], None, answer_details, headers_written['answers'], fieldnames_refs['answers'])
                                    writers['answers'].writerow(answer_details)
                                    files['answers'].flush()
                                else:
                                    writers['answers'].writerow(answer_details)
                                    files['answers'].flush()
                    
                    answers_offset += 1

            offset += 1

    finally:
        for f in files.values():
            f.close()
        print("Done.")

if __name__ == "__main__":
    main()
