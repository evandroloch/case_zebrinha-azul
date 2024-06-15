#enviar dados ao banco escolhido 
import pandas as pd
from sqlalchemy import create_engine
from yaml import safe_load

def import_config():
    with open('./config/config.yaml','r') as config:
        config=safe_load(config)
    return config

def create_connection(config):
    user=config["database"]["user"]
    password=config["database"]["password"]
    host=config["database"]["host"]
    port=config["database"]["port"]
    database=config["database"]["database"]
    conn_str = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(conn_str)
    return engine


def save_in_database(dataframe,table_name,connection):
    dataframe.to_sql(table_name, connection, index=False,if_exists="replace")
    print(f"tabela {table_name} carregada  com sucesso")

config = import_config()

connection = create_connection(config)

dataframe_weather_clean=pd.read_json('model_data/clean_data/wheater_cleaned.json')
table_wheater = 'tempo_cidades'
save_in_database(dataframe_weather_clean,table_wheater,connection)

dataframe_traffic_clean=pd.read_json('model_data/clean_data/traffic_cleaned.json')
table_traffic = 'rota_trafego'
save_in_database(dataframe_traffic_clean,table_traffic,connection)