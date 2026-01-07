# SndeskTiflux Importer

Este projeto consiste em um conjunto de scripts Python para extrair dados da API do Tiflux e consolidá-los em um formato CSV específico (modelo Sndesk).

## Funcionalidades

1.  **Importação de Dados (`import_tiflux.py`)**:
    *   Conecta-se à API v2 do Tiflux.
    *   Baixa dados de Clientes, Contatos, Endereços e Solicitantes.
    *   Salva os dados brutos em arquivos CSV separados (`clientes.csv`, `contatos.csv`, `enderecos.csv`, `solicitantes.csv`).
    *   Respeita o rate limit da API.
    *   Solicita o Bearer Token na execução.

2.  **Mesclagem de Dados (`merge_csv.py`)**:
    *   Lê os arquivos CSV gerados anteriormente.
    *   Consolida as informações em um único arquivo `modelosndesk.csv`.
    *   Remove duplicatas baseadas no CPF/CNPJ.
    *   Mapeia os campos para o layout esperado.

## Pré-requisitos

*   Python 3.x instalado.
*   Biblioteca `requests`.

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
    pip install requests
    ```

## Como Usar

### Passo 1: Importar Dados do Tiflux

Execute o script de importação:

```bash
python import_tiflux.py
```

O script solicitará o seu **Bearer Token** do Tiflux. Cole-o e pressione Enter. O processo pode demorar dependendo da quantidade de clientes, pois o script respeita o limite de requisições da API.

### Passo 2: Gerar CSV Consolidado

Após a conclusão da importação, execute o script de merge:

```bash
python merge_csv.py
```

Isso gerará o arquivo `modelosndesk.csv` na raiz do projeto, pronto para uso.

## Créditos

Desenvolvido por: **oswaldo.paulo@gmail.com**

*Este projeto foi desenvolvido com o auxílio de Inteligência Artificial.*
