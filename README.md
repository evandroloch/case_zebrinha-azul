
# Projeto de Pipeline de Dados e Dashboard Interativo

## Visão Geral

Este projeto visa criar um pipeline de dados utilizando o Apache Airflow para automatizar o processo de coleta de informações de rotas da API do Google Maps e dados climáticos das cidades ao longo dessas rotas da API Weather. Os dados são processados e armazenados em um banco de dados PostgreSQL. Um dashboard interativo é desenvolvido utilizando a biblioteca Dash para visualização dos dados climáticos das cidades presentes na rota selecionada.

## Estrutura do Projeto

### DAG do Apache Airflow

- **Tarefas**:
  1. **Pegar Parâmetros**: Obtém os parâmetros de origem e destino da rota.
  2. **Chamada das APIs**: Realiza a chamada para a API do Google Maps para obter informações da rota e, com base nos dados obtidos, faz a chamada para a API Weather para coletar dados climáticos das cidades ao longo da rota.
  3. **Limpeza de Dados**: Processa e limpa os dados coletados.
  4. **Inserção no Banco de Dados**: Insere os dados limpos no banco de dados PostgreSQL.

### Dashboard Interativo

- **Dash**: Biblioteca utilizada para criar gráficos e visualizações interativas.
- **Arquivo**: `airflow/dags/dashboard/view.py` é responsável por configurar e executar o dashboard.

### Trigger DAG

- **Arquivo**: `trigger_dag.py` aciona a execução da DAG do Airflow. Durante a execução deste arquivo, serão solicitados os parâmetros de origem e destino da rota ao usuário.

## Configuração e Execução

### Docker Compose

Para iniciar os serviços do Apache Airflow e PostgreSQL em containers Docker, utilize o seguinte comando:

```bash
docker-compose up -d
```

O arquivo `docker-compose.yaml` contém a configuração necessária para organizar a infraestrutura e executar o pipeline de dados de forma isolada e escalável.

### Dashboard Dash

Para iniciar o dashboard interativo, execute o seguinte comando:

```bash
python airflow/dags/dashboard/view.py
```

Este comando irá configurar e executar o dashboard Dash, permitindo visualizar e interagir com os gráficos de dados climáticos das cidades presentes na rota selecionada.

### Execução da DAG

Para executar a DAG do Apache Airflow e disparar o pipeline de dados, utilize o arquivo `trigger_dag.py`. Durante a execução deste arquivo, serão solicitados os parâmetros de origem e destino da rota ao usuário.

## Execução

1. **Inicialização do Ambiente**:
   - Utilize o comando `docker-compose up -d` para iniciar os serviços do Airflow e PostgreSQL.

2. **Execução da DAG**:
   - Execute o arquivo `trigger_dag.py` com Python para disparar a execução da DAG do Airflow.
   - Durante a execução, o código solicitará ao usuário os parâmetros de origem e destino da rota.

3. **Dashboard Interativo**:
   - Execute o arquivo `view.py` para abrir o dashboard Dash e visualizar os gráficos interativos dos dados climáticos das cidades presentes na rota selecionada.


