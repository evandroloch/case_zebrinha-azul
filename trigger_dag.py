import requests
import json
from datetime import datetime


AIRFLOW_URL = "http://127.0.0.1:8080/api/v1/dags/process_data_dag/dagRuns"
USERNAME = "airflow"
PASSWORD = "airflow"
print('adicionar cidade de partida')
origin= input()
print('adicionar cidade destino')
destination=input()
params = {
    "origin": origin,
    "destination": destination
}


data = {
    "conf": params,
    "dag_run_id": f"manual__{datetime.now().isoformat()}"
}


headers = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}


response = requests.post(
    AIRFLOW_URL,
    headers=headers,
    data=json.dumps(data),
    auth=(USERNAME, PASSWORD)
)


if response.status_code == 200:
    print("DAG acionada com sucesso!")
    print("Resposta:", response.json())
else:
    print("Falha ao acionar a DAG")
    print("Status Code:", response.status_code)
    print("Resposta:", response.text)
