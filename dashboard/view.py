
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
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


config = import_config()
engine = create_connection(config)

df_clima = pd.read_sql_table("tempo_cidades",engine)
df_rota = pd.read_sql('rota_trafego',engine)
df = pd.merge(df_clima, df_rota, left_on='cidade', right_on='cidade', how='inner')
df['data'] = pd.to_datetime(df['data'])


app = dash.Dash(__name__)


app.layout = html.Div([
    html.H1("Dashboard de Clima"),
    
    dcc.Graph(id='line-chart'),
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='pie-chart'),
    
    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  
])


@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graph(n):
    
    fig_line = px.line(df, x='data', y='temperatura', color='cidade',
                       title='Variação da Temperatura ao longo do tempo')

    
    fig_bar = go.Figure(data=[
        go.Bar(name='temperatura_minima', x=df['cidade'], y=df['temperatura_minima']),
        go.Bar(name='temperatura_maxima', x=df['cidade'], y=df['temperatura_maxima'])
    ])
    fig_bar.update_layout(barmode='group', title='Comparação de Temperaturas Mínimas e Máximas entre Cidades')

    
    fig_pie = px.pie(df, names='visual', title='Distribuição das Condições Climáticas', hole=0.3)
    
    return fig_line, fig_bar, fig_pie


if __name__ == '__main__':
    app.run_server(debug=True)