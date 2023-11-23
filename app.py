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
# from pypfopt import risk_models
# from pypfopt import expected_returns
# from pypfopt import plotting
# from pypfopt.efficient_frontier import EfficientFrontier

# Dataframe
##Precio
stocks = ["PG", "KO", "NSRGY", "PEP", "GE", "JNJ"]
end = datetime.datetime.now()
start = end - datetime.timedelta(days=365 * 3)
data = yf.download(stocks, start=start, end=end)["Adj Close"]
nombres = ['PrecioGE', 'PrecioJNJ', 'PrecioKO', 'PrecioNSRGY', 'PrecioPEP', 'PrecioPG']
data.columns = nombres

##Retorno
returns = data.pct_change()
nombre = ['RetornoGE', 'RetornoJNJ', 'RetornoKO', 'RetornoNSRGY', 'RetornoPEP', 'RetornoPG']
returns.columns = nombre

##Retorno max Sharpe y min varianza
mu = expected_returns.mean_historical_return(data)
sigma = risk_models.sample_cov(data)
ef = EfficientFrontier(mu,sigma)
psharpe = ef.max_sharpe()
ef = EfficientFrontier(mu,sigma)
pvol = ef.min_volatility()
r_sharpe = data.pct_change()
peso_sharpe = np.array(list(psharpe.values()))
r_sharpe["Retorno_max_sharpe"] = r_sharpe.dot(peso_sharpe)
ret_sharpe = (1+r_sharpe).cumprod()
r_vol = data.pct_change()
peso_var = np.array(list(pvol.values()))
r_vol["Retorno_min_var"] = r_vol.dot(peso_var)
ret_vol = (1+r_vol).cumprod()


a = ret_sharpe['Retorno_max_sharpe']
b = ret_vol['Retorno_min_var']

df = pd.merge(data, returns, left_index=True, right_index=True)
df['Retorno_max_sharpe']=a
df['Retorno_min_var']=b
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
    
    # Histograma Retorno Max Sharpe
    html.Div([
        dcc.Graph(id="hist-retorno-max-sharpe", figure={}, config={"displayModeBar": True, "displaylogo": False}),
    ], style={'width': '1100px', 'margin-top': '20px'}),

    # Histograma Retorno Min Var
    html.Div([
        dcc.Graph(id="hist-retorno-min-var", figure={}, config={"displayModeBar": True, "displaylogo": False}),
    ], style={'width': '1100px', 'margin-top': '20px'}),
    
])


@app.callback(
    [Output("graph-precio", "figure"),
     Output("graph-retorno", "figure"),
    Output("hist-retorno-max-sharpe", "figure"),
     Output("hist-retorno-min-var", "figure")],
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

    # Histograma Retorno Max Sharpe
    fig_hist_max_sharpe = px.histogram(df_filtered, x='Retorno_max_sharpe', nbins=10,
                                    title='Histograma Retorno Max Sharpe',
                                    color_discrete_sequence=px.colors.qualitative.Set1)
    fig_hist_max_sharpe.update_layout(bargap=0.1) 

# Histograma Retorno Min Var
    fig_hist_min_var = px.histogram(df_filtered, x='Retorno_min_var', nbins=10,
                                 title='Histograma Retorno Min Var',
                                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig_hist_min_var.update_layout(bargap=0.1)
    
    return fig_precio, fig_retorno,fig_hist_max_sharpe, fig_hist_min_var

if __name__ == '__main__':
    app.run_server(debug=False, host="192.168.0.26", port=10007)
