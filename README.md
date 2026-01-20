# SndeskTiflux Importer

Este projeto consiste em um conjunto de scripts Python para extrair dados da API do Tiflux, consolidá-los em CSV e gerar scripts SQL para migração de dados para o sistema Sndesk.

## Funcionalidades

### 1. Importação de Clientes e Contatos
*   **Script**: `import_tiflux.py`
*   **Descrição**: Conecta-se à API v2 do Tiflux e baixa dados de Clientes, Contatos, Endereços e Solicitantes.
*   **Saída**: `clientes.csv`, `contatos.csv`, `enderecos.csv`, `solicitantes.csv`.

### 2. Importação de Catálogos e Departamentos
*   **Script**: `import_catalogo.py`
*   **Descrição**: Baixa dados de Mesas (Departamentos), Catálogos (Produtos) e Itens de Catálogo (Tipos).
*   **Saída**: `mesas.csv`, `catalogos.csv`, `itensdocatalogo.csv`.

### 3. Processamento de Dados
*   **Script**: `merge_csv.py`
    *   Consolida informações de clientes em `modelosndesk.csv`.
    *   Remove duplicatas por CPF/CNPJ.
*   **Script**: `generate_sql.py`
    *   Gera `insert_dados.sql` para popular as tabelas `clientes` e `cliente_emails`.
*   **Script**: `generate_sql_departamentos.py`
    *   Gera `insert_dados_departamentos.sql` para popular as tabelas `departamentos`, `produtos`, `tipos` e seus relacionamentos (`produto_departamentos`, `tipo_produtos`).

## Pré-requisitos

*   Python 3.x instalado.
*   Biblioteca `requests`.
*   Biblioteca `pandas`.

## Instalação

1.  Clone este repositório.
2.  Crie um ambiente virtual (opcional, mas recomendado):
    ```bash
    python -m venv .venv
    # Windows
    .venv\Scripts\activate
    # Linux/Mac
    source .venv/bin/activate
    ```
3.  Instale as dependências:
    ```bash
    pip install requests pandas
    ```

## Como Usar

### Passo 1: Extrair Dados da API

Execute os scripts de importação. Você precisará de um **Bearer Token** válido do Tiflux.

```bash
# Importar Clientes
python import_tiflux.py

# Importar Catálogos/Departamentos
python import_catalogo.py
```

### Passo 2: Gerar Arquivos de Migração

Após baixar os dados, gere os arquivos finais:

```bash
# Gerar CSV consolidado de clientes
python merge_csv.py

# Gerar SQL de Clientes
python generate_sql.py

# Gerar SQL de Departamentos e Produtos
python generate_sql_departamentos.py
```

Os arquivos gerados (`.csv` e `.sql`) estarão na raiz do projeto.

## Créditos

Desenvolvido por: **oswaldo.paulo@gmail.com**

*Este projeto foi desenvolvido com o auxílio de Inteligência Artificial.*
