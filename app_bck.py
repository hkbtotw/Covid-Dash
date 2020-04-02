import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output

from DataEngine_v2 import loadData

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}



allData = loadData("time_series_covid19_confirmed_global.csv", "CumConfirmed") \
    .merge(loadData("time_series_covid19_deaths_global.csv", "CumDeaths")) \
    .merge(loadData("time_series_covid19_recovered_global.csv", "CumRecovered"))

countries = allData['Country/Region'].unique()
countries.sort()

print(allData)


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div(
    #style={ 'font-family':"Courier New, monospace" },
    style={ 'marginLeft':'1.5%','marginRight':'1.5%','marginBottom':'0.8%' },

    children=[
    html.H1('Case History of the Coronavirus (COVID-19)'),
    html.Div(  className="row", 
        children=[
        html.Div( #className="four columns", 
            style={ 'width':'30.0%','backgroundColor':'#ffffff','display':'inline-block',
                'marginRight':'0.8%','verticalAlign':'top', 'box-shadow':'0px 0px 10px #ededee','border':'1px solid #ededee' },
            children=[
            html.H5('Country'),
            dcc.Dropdown(
                id='country',
                options=[{'label':c, 'value':c} for c in countries],
                value='Italy'
            )
        ]),
        html.Div( #className="four columns",
            style={ 'width':'30.0%','backgroundColor':'#ffffff','display':'inline-block',
                'marginRight':'0.8%','verticalAlign':'top', 'box-shadow':'0px 0px 10px #ededee','border':'1px solid #ededee' },
            children=[
            html.H5('State / Province'),
            dcc.Dropdown(
                id='state'
            )
        ]),
        html.Div( #className="four columns", 
            style={ 'width':'30.0%','backgroundColor':'#ffffff','display':'inline-block',
                'marginRight':'0.8%','verticalAlign':'top', 'box-shadow':'0px 0px 10px #ededee','border':'1px solid #ededee' },
            children=[
            html.H5('Selected Metrics'),
            dcc.Checklist(
                id='metrics',
                options=[{'label':m, 'value':m} for m in ['Confirmed', 'Deaths', 'Recovered']],
                value=['Confirmed', 'Deaths']
            )
        ])
    ]),

    dcc.Graph(
        id="plot_cum_metrics",
        config={ 'displayModeBar': False }
    )
])

@app.callback(
    [Output('state', 'options'), Output('state', 'value')],[Input('country', 'value')]
)
def update_states(country):
    states = list(allData.loc[allData['Country/Region'] == country]['Province/State'].unique())
    states.insert(0, '<all>')
    states.sort()
    state_options = [{'label':s, 'value':s} for s in states]
    state_value = state_options[0]['value']
    return state_options, state_value

def nonreactive_data(country, state):
    data = allData.loc[allData['Country/Region'] == country].drop('Country/Region', axis=1)
    print(data.columns)

    return data

def barchart(data, metrics, prefix, yaxisTitle):
    print(data.date, '== date ==  ',len(data.date))
    print(' prefix : ', prefix)
    print(' metrics : ', metrics[0])
    
    col=prefix+metrics[0]
    print(' pm :: ',col, ' ==> ',type(col))
    print(data.CumConfirmed, ' ++ data ++  ',len(data.CumConfirmed))

    figure = go.Figure(data=[
        go.Bar( 
            name=metric, x=data.date, y=data.CumConfirmed,
            marker_line_color='rgb(0,0,0)', marker_line_width=1,
            marker_color={ 'Confirmed':'rgb(100,140,240)'}[metric]) for metric in metrics])
    #figure.update_layout( 
    #          barmode='group', legend=dict(x=.05, y=0.95, font={'size':15}, bgcolor='rgba(240,240,240,0.5)'), 
    #          plot_bgcolor='#FFFFFF', font=tickFont).update_xaxes(title="", tickangle=-90, type='category', showgrid=True, gridcolor='#DDDDDD', 
    #          tickfont=tickFont, ticktext=data.dateStr, tickvals=data.date).update_yaxes(title=yaxisTitle, showgrid=True, gridcolor='#DDDDDD')
    return figure



@app.callback(
    Output('plot_cum_metrics', 'figure'), 
    [Input('country', 'value'), Input('state', 'value'), Input('metrics', 'value')]
)
def update_plot_cum_metrics(country, state, metrics):
    data = nonreactive_data(country, state)
    return barchart(data, metrics, prefix="Cum", yaxisTitle="Cumulated Cases")

server = app.server

if __name__ == '__main__':
    #app.run_server(host="0.0.0.0", debug=True)
    app.run_server(debug=False)
