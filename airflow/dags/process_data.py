from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests
import json
import pandas as pd
from sqlalchemy import create_engine
from yaml import safe_load
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import os

def get_parameters(**kwargs):
    params = kwargs['dag_run'].conf
    for key, value in params.items():
        kwargs['ti'].xcom_push(key=key, value=value)


# Function to import configuration
def import_config():
    with open('dags/config/config.yaml', 'r') as config:
        config = safe_load(config)
    return config

# Function to create a database connection
def create_connection(config):
    user = config["database"]["user"]
    password = config["database"]["password"]
    host = config["database"]["host"]
    port = config["database"]["port"]
    database = config["database"]["database"]
    conn_str = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(conn_str)
    return engine

# Function to fetch and save data
def fetch_and_save_data(origin, destination):
    config = import_config()
    
    def get_weather(city, config):
        url_base = config["openweather"]['base_url']
        api_key = config["openweather"]['api_key']
        params = {'q': city, 'appid': api_key, 'units': 'metric'}
        response = requests.get(url_base, params=params)
        return response.json()
    
    def format_data(data):
        formatted_data = {"City": data["city"]["name"], "Country": data["city"]["country"], "Forecast": []}
        for entry in data["list"]:
            forecast_entry = {
                "DateTime": entry["dt_txt"],
                "Temperature": entry["main"]["temp"],
                "Feels Like": entry["main"]["feels_like"],
                "Min Temperature": entry["main"]["temp_min"],
                "Max Temperature": entry["main"]["temp_max"],
                "Pressure": entry["main"]["pressure"],
                "Humidity": entry["main"]["humidity"],
                "Weather": entry["weather"][0]["description"],
                "Wind Speed": entry["wind"]["speed"],
                "Wind Direction": entry["wind"]["deg"]
            }
            formatted_data["Forecast"].append(forecast_entry)
        return formatted_data
    
    def save_data_as_json(data, file_path):
        with open(file_path, "w") as json_file:
            json.dump(data, json_file, indent=4)

    def get_cities_along_route(origin, destination, config):
        api_key = config["google_maps"]["api_key"]
        directions_url = config["google_maps"]["base_url_directions"]
        geocoding_url = config["google_maps"]["base_url_geocode"]
        params = {"origin": origin, "destination": destination, "key": api_key}
        response = requests.get(directions_url, params=params)
        directions_data = response.json()

        if directions_data["status"] == "OK":
            steps = directions_data["routes"][0]["legs"][0]["steps"]
            route_points = [(step["end_location"]["lat"], step["end_location"]["lng"]) for step in steps]
            cities = []

            for point in route_points:
                lat, lng = point
                geocoding_params = {"latlng": f"{lat},{lng}", "key": api_key}
                geocoding_response = requests.get(geocoding_url, params=geocoding_params)
                geocoding_data = geocoding_response.json()

                if geocoding_data["status"] == "OK":
                    for result in geocoding_data["results"]:
                        for component in result["address_components"]:
                            if "locality" in component["types"] and component["long_name"] not in cities:
                                cities.append(component["long_name"])
            return cities

    def get_time_journey_to_city(origin, destination, config):
        index_route = "|".join([origin, destination])
        waypoints = get_cities_along_route(origin, destination, config)
        api_key = config["google_maps"]["api_key"]
        waypoints_str = "|".join(waypoints)
        directions_url = f"{config['google_maps']['base_url_directions']}?origin={origin}&destination={destination}&waypoints={waypoints_str}&departure_time=now&key={api_key}"
        response = requests.get(directions_url)
        directions = response.json()
        
        if directions['status'] == 'OK':
            time_accumulator = timedelta()
            arrival_data = []

            for leg in directions["routes"][0]["legs"]:
                duration_in_seconds = leg["duration"]["value"]
                time_accumulator += timedelta(seconds=duration_in_seconds)
                end_address = leg["end_address"]
                end_location = leg["end_location"]
                lat = end_location["lat"]
                lon = end_location["lng"]

                arrival_data.append({
                    'route': index_route,
                    "city": end_address.split(',')[0],
                    "latitude": lat,
                    "longitude": lon,
                    "duration_of_the_journey": str(time_accumulator)
                })
            return arrival_data

    config = import_config()
    cities = get_cities_along_route(origin, destination, config)
    data = get_time_journey_to_city(origin, destination, config)
    save_data_as_json(data, 'dags/extract_data/trafic/arrive_time.json')
    
    for city in cities:
        weather_data = get_weather(city, config)
        formatted_weather_data = format_data(weather_data)
        save_data_as_json(formatted_weather_data, f"dags/extract_data/weather/weather_{city}.json")

# Function to process data
def process_data(src_traffic, dest_traffic, src_weather, dest_weather):
    def read_all_files_in_pandas(directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        dataframes = [pd.read_json(os.path.join(directory, file)) for file in files]
        combined_df = pd.concat(dataframes, ignore_index=True)
        combined_df = pd.concat([pd.json_normalize(combined_df['Forecast']), combined_df], axis=1).drop(columns='Forecast')
        return combined_df

    def drop_duplicates_drop_null(dataframe):
        dataframe.drop_duplicates(inplace=True)
        dataframe.dropna(inplace=True)
        return dataframe

    def rename_columns(dataframe, columns_renamed):
        dataframe.columns = columns_renamed
        return dataframe

    def save_dataframe(dataframe, path):
        dataframe.to_json(path)

    columns_weather = ['data', 'temperatura', 'sensacao_termica', 'temperatura_minima', 'temperatura_maxima', 
                       'pressao_atmosferica', 'humidade', 'visual', 'velocidade_vento', 'direcao_vento', 'cidade', 'pais']
    columns_traffic = ['rota', 'cidade', 'latitude', 'longitude', 'duracao_do_percusso']
    
    dataframe_traffic = pd.read_json(src_traffic)
    dataframe_traffic = drop_duplicates_drop_null(dataframe_traffic)
    dataframe_traffic = rename_columns(dataframe_traffic, columns_traffic)
    save_dataframe(dataframe_traffic, dest_traffic)
    
    dataframe_weather = read_all_files_in_pandas(src_weather)
    dataframe_weather = drop_duplicates_drop_null(dataframe_weather)
    dataframe_weather = rename_columns(dataframe_weather, columns_weather)
    save_dataframe(dataframe_weather, dest_weather)

# Function to send data to the database
def send_data_to_database():
    config = import_config()
    connection = create_connection(config)

    dataframe_weather_clean = pd.read_json('dags/model_data/clean_data/weather.json')
    table_weather = 'tempo_cidades'
    dataframe_weather_clean.to_sql(table_weather, connection, index=False, if_exists="append")
    print(f"Table {table_weather} loaded successfully")

    dataframe_traffic_clean = pd.read_json('dags/model_data/clean_data/arrive_time.json')
    table_traffic = 'rota_trafego'
    dataframe_traffic_clean.to_sql(table_traffic, connection, index=False, if_exists="append")
    print(f"Table {table_traffic} loaded successfully")



# Airflow DAG definition
default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('process_data_dag', default_args=default_args, schedule_interval=None) as dag:
    get_params = PythonOperator(
        task_id='get_parameters',
        python_callable=get_parameters,
        provide_context=True
    )
       
    fetch_and_save_data_task = PythonOperator(
        task_id='fetch_and_save_data',
        python_callable=fetch_and_save_data,
        provide_context=True,
        op_args=['{{ ti.xcom_pull(task_ids="get_parameters", key="origin") }}','{{ ti.xcom_pull(task_ids="get_parameters", key="destination") }}']
    )

    process_data_task = PythonOperator(
        task_id='process_data',
        python_callable=process_data,
        op_args=[
            'dags/extract_data/trafic/arrive_time.json',  # src_traffic
            'dags/model_data/clean_data/arrive_time.json',  # dest_traffic
            'dags/extract_data/weather/',  # src_weather
            'dags/model_data/clean_data/weather.json'  # dest_weather
        ],
    )

    send_data_to_database_task = PythonOperator(
        task_id='send_data_to_database',
        python_callable=send_data_to_database
    )


    get_params>>fetch_and_save_data_task >> process_data_task >> send_data_to_database_task
