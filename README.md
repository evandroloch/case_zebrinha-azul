# Projeto de Pipeline de Dados e Dashboard Interativo

## Visão Geral

Este projeto tem como objetivo criar um pipeline de dados utilizando o Apache Airflow para orquestrar tarefas que extraem dados de uma API, limpam esses dados e os inserem em um banco de dados. Além disso, um dashboard interativo é criado localmente usando a biblioteca Dash para visualização dos dados processados.

## Estrutura do Projeto

### DAG do Airflow

- **Tarefa de Extração**: Coleta dados de uma API.
- **Tarefa de Limpeza**: Processa e limpa os dados coletados.
- **Tarefa de Carregamento**: Insere os dados limpos em um banco de dados PostgreSQL.

### Dashboard Interativo

- **Dash**: Biblioteca utilizada para criar gráficos interativos a partir dos dados armazenados no banco de dados.

## Requisitos

- **Docker** e **Docker Compose**: Para gerenciar os serviços do Airflow e PostgreSQL.
- **Apache Airflow**: Para orquestração do pipeline de dados.
- **PostgreSQL**: Banco de dados para armazenar os dados processados.
- **Dash**: Biblioteca para criação do dashboard.
- **Plotly**: Biblioteca para gráficos interativos no Dash.
- **SQLAlchemy**: Biblioteca para conexão com o banco de dados PostgreSQL.
- **Pandas**: Biblioteca para manipulação de dados.

## Configuração e Execução

### 1. Docker Compose

#### Arquivo `docker-compose.yaml`

Crie um arquivo `docker-compose.yaml` na pasta `airflow` com o conteúdo adequado para configurar os serviços do Airflow e PostgreSQL.

#### Passos Iniciais

1. Instale o Docker.
2. Posicione o terminal na pasta `airflow` e execute o comando:

    ```bash
    docker compose up -d
    ```

### 2. Disparar a DAG

1. Rode o arquivo `trigger_dag.py`.
2. Quando solicitado, insira os dados de origem da rota e destino.

### 3. Dashboard

Para executar o dashboard, rode o arquivo `view.py` na pasta `airflow/dags/dashboard`.

```bash
python airflow/dags/dashboard/view.py
```

O dashboard estará disponível em `http://127.0.0.1:8050`.

