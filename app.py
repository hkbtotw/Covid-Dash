import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objects as go
from dash.dependencies import Input, Output
import pandas as pd
from datetime import datetime

from Operation_v1 import PrepData, MakePlot

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

tickFont = {'size':12, 'color':"rgb(30,30,30)", 'family':"Courier New, monospace"}

prepData=PrepData()
makePlot=MakePlot()
dfLoad=prepData.LoadData()

pConfirmed, pRecovered, pDeaths, daysOutbreak, maxDate, Confirmed, Recovered, Deaths, newConfirmed, newCsym, newRecovered, newRsym, newDeaths, newDsym=prepData.NumberPlateCalculation(dfLoad)

##########  Plot

fig_confirmed, fig_combine, fig_rate=makePlot.ProgressUpdatePlot(dfLoad)


#########
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

# Title to appear at browser tab
app.title = 'Coronavirus COVID-19 Monitor'


app.layout = html.Div(
    style={ 'backgroundColor':'#fafbfd'},

    children=[

    ####  Title
        html.Div(style={'marginRight': '1.5%',},
            id="header",
            children=[
            html.H1('Coronavirus (COVID-19) Outbreak Monitoring'),
            html.P(
                    id="description",
                    children=dcc.Markdown(
                      children=(
                        '''
                        On Dec 31, 2019, the World Health Organization (WHO) was informed 
                        an outbreak of “pneumonia of unknown cause” detected in Wuhan, Hubei Province, China. 
                        The virus that caused the outbreak of COVID-19 was lately known as _severe acute respiratory syndrome coronavirus 2_ (SARS-CoV-2). 
                        The WHO declared the outbreak to be a Public Health Emergency of International Concern on 
                        Jan 30, 2020 and recognized it as a pandemic on Mar 11, 2020. As of {}, there are {:,d} cases of COVID-19 confirmed globally.
                        '''.format(maxDate, Confirmed),
                      )
                    )
                ),
                     ]),
        ######## Number plate 
        html.Div( id='number-plate',
            style={ 'marginLeft':'1.5%','marginRight':'1.5%','marginBottom':'0.8%' },
            children=[
         ######### 1st box
            html.Div( id='outbreakDay',
            style={ 'width':'24.0%','backgroundColor':'#ffffff','display':'inline-block',
                'marginRight':'0.8%','verticalAlign':'top', 'box-shadow':'0px 0px 10px #ededee','border':'1px solid #ededee' },
            children=[
                html.H3(style={'textAlign': 'center','fontWeight': 'bold', 'color': '#2674f6'},
                     children=[
                              html.P(style={'padding': '.5rem'},children='Update at  {}'.format(maxDate)),
                             '{}'.format(daysOutbreak),
                              ]),
                html.H5(style={'textAlign': 'center', 'color': '#2674f6', 'padding': '.1rem'},
                                               children='days since outbreak began at  {}'.format(prepData.outbreakStart))
                ]),
        ####### 2nd box
        html.Div(id='confirmed',
            style={ 'width':'24.0%','backgroundColor':'#ffffff','display':'inline-block',
                'marginRight':'0.8%','verticalAlign':'top', 'box-shadow':'0px 0px 10px #ededee','border':'1px solid #ededee' },
            children=[
                html.H3(style={'textAlign': 'center','fontWeight': 'bold', 'color': '#d7191c'},
                     children=[
                              html.P(style={'padding': '.5rem'},children='{} {:,d} in the past 24h ({} {:.1%}) '.format(newCsym,newConfirmed,newCsym,pConfirmed)),
                             '{:,d}'.format(Confirmed),
                              ]),
                html.H5(style={'textAlign': 'center', 'color': '#d7191c', 'padding': '.1rem'},
                                               children='confirmed cases'),
 
                    ]),
        ######## Recovered
        html.Div(id='recovered',
            style={ 'width':'24.0%','backgroundColor':'#ffffff','display':'inline-block',
                'marginRight':'0.8%','verticalAlign':'top', 'box-shadow':'0px 0px 10px #ededee','border':'1px solid #ededee' },
            children=[
                html.H3(style={'textAlign': 'center','fontWeight': 'bold', 'color': '#1a9622'},
                     children=[
                              html.P(style={'padding': '.5rem'},children='{} {:,d} in the past 24h  ({} {:.1%}) '.format(newRsym,newRecovered, newRsym, pRecovered)),
                             '{:,d}'.format(Recovered),
                              ]),
                html.H5(style={'textAlign': 'center', 'color': '#1a9622', 'padding': '.1rem'},
                                               children='recovered cases'),

        ]),
        ############ Deaths
        html.Div( id='death',
            style={ 'width':'24.0%','backgroundColor':'#ffffff','display':'inline-block',
                'marginRight':'0.8%','verticalAlign':'top', 'box-shadow':'0px 0px 10px #ededee','border':'1px solid #ededee' },
            children=[
              html.H3(style={'textAlign': 'center','fontWeight': 'bold', 'color': '#6c6c6c'},
                     children=[
                              html.P(style={'padding': '.5rem'},children='{} {:,d} in the past 24h  ({} {:.1%}) '.format(newDsym,newDeaths, newDsym, pDeaths)),
                             '{:,d}'.format(Deaths),
                              ]),
                html.H5(style={'textAlign': 'center', 'color': '#6c6c6c', 'padding': '.1rem'},
                                               children='death cases'),
                    ]),
        #################  #  Number Plate

        ########## Plot
        html.Div(
            id='dcc-plot',
            style={'marginLeft': '1.5%', 'marginRight': '1.5%', 'backgroundColor': '#ffffff',
                   'marginBottom': '.8%', 'marginTop': '.5%',
                   'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'
                },
                 children=[
                     ############ fig_confirmed
                     html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                                'marginRight': '.8%', 'verticalAlign': 'top',
                                #'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'
                                },
                         children=[
                                  html.H5(
                                    style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                           'color': '#292929', 'padding': '1rem', 'marginBottom': '0','marginTop': '0'},
                                    children='Confirmed Case Timeline'),
                                  dcc.Graph(
                                    style={'height': '300px'}, 
                                    figure=fig_confirmed),
                                  ]),
                    ############# fig
                     html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                                'marginRight': '.8%', 'verticalAlign': 'top',
                                #'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'
                                },
                         children=[
                                  html.H5(
                                    style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                           'color': '#292929', 'padding': '1rem', 'marginBottom': '0','marginTop': '0'},
                                    children='Active/Recovered/Death Case Timeline'),
                                  dcc.Graph(
                                    style={'height': '300px'}, 
                                    figure=fig_combine),
                                  ]),
                    ############### fig
                     html.Div(
                         style={'width': '32.79%', 'display': 'inline-block',
                                'verticalAlign': 'top',
                                #'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'
                                },
                         children=[
                                  html.H5(
                                    style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                           'color': '#292929', 'padding': '1rem', 'marginBottom': '0','marginTop': '0'},
                                    children='Death Rate (%) Timeline'),
                                  dcc.Graph(
                                    style={'height': '300px'}, 
                                    figure=fig_rate),
                                  ]),
                     ]),  ### end fig


        ########### Plot end

        ]), # Children outermost
        ##########################

]) # outter most

"""
def barchart(data, metrics, prefix, yaxisTitle):
    #print(data.date, '== date ==  ',len(data.date))
    #print(' prefix : ', prefix)
    #print(' metrics : ', metrics[0])
    
    col=prefix+metrics[0]
    #print(' pm :: ',col, ' ==> ',type(col))
    #print(data.CumConfirmed, ' ++ data ++  ',len(data.CumConfirmed))

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
"""
server = app.server

if __name__ == '__main__':
    #app.run_server(host="0.0.0.0", debug=True)
    app.run_server(debug=False)
