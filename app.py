# Librerías utilizadas
import dash
from dash import dcc
from dash import html
from dash import dash_table
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
import yfinance as yf
import datetime

# Dataframe
stocks = ["PG", "KO", "NSRGY", "PEP", "GE", "JNJ"]
end = datetime.datetime.now()
start = end - datetime.timedelta(days=365 * 3)
data = yf.download(stocks, start=start, end=end)["Adj Close"]
nombres = ['PrecioGE', 'PrecioJNJ', 'PrecioKO', 'PrecioNSRGY', 'PrecioPEP', 'PrecioPG']
data.columns = nombres

returns = data.pct_change()
nombre = ['RetornoGE', 'RetornoJNJ', 'RetornoKO', 'RetornoNSRGY', 'RetornoPEP', 'RetornoPG']
returns.columns = nombre

df = pd.merge(data, returns, left_index=True, right_index=True)
df = df.iloc[1:]

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

#Dashboard

app.title = "Dashboard"
app.layout = html.Div([
    html.Div([
        # Slider para cambiar las fechas
        dcc.RangeSlider(
            id='fechas-slider',
            marks={i: date.strftime('%Y-%m-%d') for i, date in enumerate(df.index)},
            min=0,
            max=len(df.index) - 1,
            step=1,
            value=[0, len(df.index) - 1],
            tooltip={"placement": "bottom", "always_visible": True},
        ),
    ]),

    # Dropdown Precios
    html.Div([
        dcc.Dropdown(
            id='dropdown-precio',
            options=[{'label': x, 'value': x} for x in nombres],
            value=['PrecioGE','PrecioPEP', 'PrecioPG'], 
            multi=True,
            style={'width': '50%'},
        ),
    ], style={'margin-top': '10px'}),

    # Dropdown Retorno
    html.Div([
        dcc.Dropdown(
            id='dropdown-retorno',
            options=[{'label': x, 'value': x} for x in nombre],
            value=['RetornoGE', 'RetornoJNJ', 'RetornoKO'],  
            multi=True,
            style={'width': '50%'},
        ),
    ], style={'margin-top': '10px'}),

    # Gráfica Precio
    html.Div([
        dcc.Graph(id="graph-precio", figure={}, config={"displayModeBar": True, "displaylogo": False}),
    ], style={'width': '1100px'}),

    # Gráfica Retorno
    html.Div([
        dcc.Graph(id="graph-retorno", figure={}, config={"displayModeBar": True, "displaylogo": False}),
    ], style={'width': '1100px'}),
])


@app.callback(
    [Output("graph-precio", "figure"),
     Output("graph-retorno", "figure")],
    [Input("fechas-slider", "value"),
     Input("dropdown-precio", "value"),
     Input("dropdown-retorno", "value")]
)
def update_graph(selected_indices, selected_precios, selected_retornos):
    start_date = df.index[selected_indices[0]]
    end_date = df.index[selected_indices[1]]
    df_filtered = df.loc[start_date:end_date]

    # Gráfica Precio
    fig_precio = px.line(df_filtered, x=df_filtered.index, y=selected_precios, title='Precios')

    # Gráfica Retorno
    fig_retorno = px.line(df_filtered, x=df_filtered.index, y=selected_retornos, title='Retornos')

    return fig_precio, fig_retorno

if __name__ == '__main__':
    app.run_server(debug=False, host="192.168.0.26", port=10007)
