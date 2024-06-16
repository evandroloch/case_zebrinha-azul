
import pandas as pd

import os
def read_all_files_in_pandas(directory):
    
    files = [f for f in os.listdir(directory)]

    
    dataframes = []

    for file in files:
        
        dataframe = pd.read_json(os.path.join(directory, file))
        
        dataframes.append(dataframe)

    
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df=pd.concat([pd.json_normalize(combined_df['Forecast']),combined_df],axis=1).drop(columns='Forecast')
    
    return combined_df


def drop_duplicates_drop_null(dataframe):
    
    dataframe.drop_duplicates(inplace=True)
    
    dataframe.dropna(inplace=True)
    return dataframe


def rename_colums(dataframe,columns_renamed):
    dataframe.columns = columns_renamed
    return dataframe


def save_dataframe(dataframe,path):
    dataframe.to_json(path)

    
columns_weather=['data','temperatura','sensacao_termica','temperatura_minima','temperatura_maxima','pressao_atmosferica','humidade','visual','velocidade_vento','direcao_vento','cidade','pais']
columns_traffic=['rota ','cidade','latitude','longitude','duracao_do_percusso']
path_weather_cleaned='./model_data/clean_data/weather.json'
path_traffic_cleaned='./model_data/clean_data/arrive_time.json'

dataframe_trafic = pd.read_json("./extract_data/trafic/arrive_time.json")
dataframe_trafic = drop_duplicates_drop_null(dataframe_trafic)
dataframe_trafic = rename_colums(dataframe_trafic,columns_traffic)
save_dataframe(dataframe_trafic,path_traffic_cleaned)


dataframe_weather=read_all_files_in_pandas('extract_data/weather/')
dataframe_weather = drop_duplicates_drop_null(dataframe_weather)
dataframe_weather = rename_colums(dataframe_weather,columns_weather)
save_dataframe(dataframe_weather,path_weather_cleaned)
