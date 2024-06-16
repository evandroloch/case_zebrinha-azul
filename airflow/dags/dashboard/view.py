import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from sqlalchemy import create_engine

def create_connection():
    user = 'airflow'
    password = 'airflow'
    host = '172.18.0.3'
    port = '5432'
    database = 'airflow'
    conn_str = f'postgresql://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(conn_str)
    return engine

engine = create_connection()

# Carregar dados iniciais
df_clima = pd.read_sql_table("tempo_cidades", engine)
df_rota = pd.read_sql('rota_trafego', engine)
df = pd.merge(df_clima, df_rota, left_on='cidade', right_on='cidade', how='inner')
df['data'] = pd.to_datetime(df['data'])

# Inicialização do aplicativo Dash
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Dashboard de Clima"),

    dcc.Dropdown(
        id='rota-dropdown',
        options=[{'label': rota, 'value': rota} for rota in df['rota'].unique()],
        value=df['rota'].unique()[0],
        clearable=False
    ),
    
    dcc.Graph(id='line-chart'),
    dcc.Graph(id='bar-chart'),
    dcc.Graph(id='pie-chart'),

    dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  
])

@app.callback(
    [Output('line-chart', 'figure'),
     Output('bar-chart', 'figure'),
     Output('pie-chart', 'figure')],
    [Input('interval-component', 'n_intervals'),
     Input('rota-dropdown', 'value')]
)
def update_graph(n, selected_rota):
    engine = create_connection()

    df_clima = pd.read_sql_table("tempo_cidades", engine)
    df_rota = pd.read_sql('rota_trafego', engine)
    df = pd.merge(df_clima, df_rota, left_on='cidade', right_on='cidade', how='inner')
    df['data'] = pd.to_datetime(df['data'])

    # Filtrar dados pela rota selecionada
    df_filtered = df[df['rota'] == selected_rota]

    # Gráfico de linha para variação da temperatura ao longo do tempo
    fig_line = px.line(df_filtered, x='data', y='temperatura', color='cidade',
                       title='Variação da Temperatura ao longo do tempo')

    # Gráfico de barras para comparação de temperaturas mínimas e máximas entre cidades
    fig_bar = go.Figure(data=[
        go.Bar(name='temperatura_minima', x=df_filtered['cidade'], y=df_filtered['temperatura_minima']),
        go.Bar(name='temperatura_maxima', x=df_filtered['cidade'], y=df_filtered['temperatura_maxima'])
    ])
    fig_bar.update_layout(barmode='group', title='Comparação de Temperaturas Mínimas e Máximas entre Cidades')

    # Gráfico de pizza para distribuição das condições climáticas
    fig_pie = px.pie(df_filtered, names='visual', title='Distribuição das Condições Climáticas', hole=0.3)

    return fig_line, fig_bar, fig_pie

if __name__ == '__main__':
    app.run_server(debug=True)
