import pandas as pd
import os

def merge_specific_files(file_list, output_file):
    print(f"--------------------------------------------------")
    print(f"Processando arquivos para gerar: {output_file}")
    
    dfs = []
    found_files = 0
    
    for file_name in file_list:
        if os.path.exists(file_name):
            print(f"  Lendo {file_name}...")
            try:
                # Tenta ler com utf-8, se falhar tenta latin1
                try:
                    df = pd.read_csv(file_name, encoding='utf-8')
                except UnicodeDecodeError:
                    print(f"  UTF-8 falhou para {file_name}, tentando latin1...")
                    df = pd.read_csv(file_name, encoding='latin1')
                
                dfs.append(df)
                found_files += 1
            except Exception as e:
                print(f"  Erro ao ler {file_name}: {e}")
        else:
            print(f"  Aviso: Arquivo {file_name} não encontrado.")

    if not dfs:
        print("  Nenhum arquivo válido encontrado para este grupo.")
        return

    print(f"  Concatenando {found_files} arquivos...")
    combined_df = pd.concat(dfs, ignore_index=True)
    
    total_rows = len(combined_df)
    combined_df.drop_duplicates(inplace=True)
    dedup_rows = len(combined_df)
    
    print(f"  Linhas: {total_rows} -> Após remover duplicatas: {dedup_rows}")
    
    try:
        combined_df.to_excel(output_file, index=False)
        print(f"  Sucesso: {output_file} criado.")
    except ImportError:
        print("  Erro: Biblioteca 'openpyxl' não instalada. Execute: pip install openpyxl")
    except Exception as e:
        print(f"  Erro ao salvar Excel: {e}")

def main():
    # 1. Tickets (1-4) -> ticket.xlsx
    tickets = [f'tickets_{i}.csv' for i in range(1, 5)]
    merge_specific_files(tickets, 'tickets.xlsx')
    
    # 2. Ticket Files (1-4) -> ticket_files.xlsx (Corrigido de ticket_fliex.xlsx)
    ticket_files = [f'ticket_files_{i}.csv' for i in range(1, 5)]
    merge_specific_files(ticket_files, 'ticket_files.xlsx')
    
    # 3. Respostas (1-4) -> respostas.xlsx (Corrigido de repostas.xlsx)
    respostas = [f'respostas_{i}.csv' for i in range(1, 5)]
    merge_specific_files(respostas, 'respostas.xlsx')

if __name__ == "__main__":
    main()
