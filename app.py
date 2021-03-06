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

# Declare Class
prepData=PrepData()
makePlot=MakePlot()

# Data Processing
dfLoad=prepData.LoadData_Timeline()
dfLoad_2=prepData.LoadData_Casesum()
#dfLoad_4=prepData.LoadData_CaseDesc() # cannot include for heroku web app , it makes workers idle longer than 30 sec so timeout
prvDict, latDict, lonDict, dfLockdown=prepData.Load_prvDict()
dfAnn=prepData.LoadData_CaseDesc_Excel()
dfScr=prepData.LoadData_CovidScreeningBKK_Excel()
dfLoad_3=makePlot.LatLon_Province(dfLoad_2, prvDict, latDict, lonDict)

pConfirmed, pRecovered, pDeaths, daysOutbreak, maxDate, Confirmed, Recovered, Deaths, newConfirmed, newCsym, newRecovered, newRsym, newDeaths, newDsym=prepData.NumberPlateCalculation(dfLoad)
dfTrend=prepData.CalcTrendTable(dfLoad)

# Prepare Plot

fig_confirmed, fig_combine, fig_rate, fig_confirmedChange=makePlot.ProgressUpdatePlot(dfLoad)
fig_curve_tab=makePlot.TrendPlot(dfTrend, daysOutbreak)
fig_map=makePlot.MapPlot(dfLoad_3)
fig_mapAnn=makePlot.MapPlot_Announcement(dfAnn, dfScr, dfLockdown)  # map-ann

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
                        Jan 30, 2020 and recognized it as a pandemic on Mar 11, 2020. As of {}, there are {:,d} cases of COVID-19 confirmed in Thailand.
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
        ######################### Curve plot
        html.Div(
            id='dcc-curve',
            style={'marginLeft': '1.5%', 'marginRight': '1.5%', 'marginBottom': '.5%'},
                 children=[
                     html.Div(style={'width': '48.31%', 'marginRight': '.8%', 'display': 'inline-block', 'verticalAlign': 'top',
                                     'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee',
                                     },
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0', 'marginTop': '0'},
                                               children='Confirmed case trajectories'),
                                  dcc.Graph(
                                      id='fig_curve_tab',
                                      style={'height': '300px'},
                                      figure=fig_curve_tab),
                                 
                                      ], ###  children
                                  ),  ### html.div
          
                                             
                     html.Div(style={'width': '48.31%', 'marginRight': '.8%', 'display': 'inline-block', 'verticalAlign': 'top',
                                     'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee',
                                     },
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0', 'marginTop': '0'},
                                               children='%Change (from yesterday) of daily confirmed case'),
                                    dcc.Graph(
                                      id='fig_confirmedChange1',
                                      style={'height': '300px'}                                      ,
                                      figure=fig_confirmedChange), 
                                 
                                      ], ###  children
                                  ),  ### html.div


                                 ], ### children



                              ),
                    ##############  end curve plot
        ##### map plot
        html.Div(
            id='dcc-map',
            style={'marginLeft': '1.5%', 'marginRight': '1.5%', 'marginBottom': '.5%'},
                 children=[
                     html.Div(style={'width': '48.31%', 'marginRight': '.8%', 'display': 'inline-block', 'verticalAlign': 'top',
                                     'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee',
                                     },
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0', 'marginTop': '0'},
                                               children='#Confirmed case by Province'),
                                  dcc.Graph(
                                      id='map',
                                      style={'height':'500'},
                                      figure=fig_map
                                    ),    
                          
                                      ]  ###Children

                                      
                                  ),   #### Div inside
                                  
                      html.Div(style={'width': '48.31%', 'marginRight': '.8%', 'display': 'inline-block', 'verticalAlign': 'top',
                                     'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee',
                                     },
                              children=[
                                  html.H5(style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0', 'marginTop': '0'},
                                               children='Locations by Incidents (based on Accouncement on Mar 29,2020) and Screening points in BKK'),
                                  dcc.Graph(
                                      id='map-ann',
                                      style={'height':'500'},
                                      figure=fig_mapAnn
                                    ),    
                          
                                      ]  ####  children inside 2
                                      
                                  ), #### div inside 2
                                  
                              ]    ### children outside 2      



                          ), ### Div outside
                    ##############  end map plot
        #### Start Histogram plot
        #html.Div(
        #    id='dcc-histogram',
        #    style={'marginLeft': '1.5%', 'marginRight': '1.5%', 'marginBottom': '.5%'},
        #    children=[
        #    html.Div(style={'width': '48.31%', 'marginRight': '.8%', 'display': 'inline-block', 'verticalAlign': 'top',
        #                             'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee',
        #                             },
        #    children=[                                  
        #        html.H5(style={'textAlign': 'center', 'backgroundColor': '#ffffff',
        #            'color': '#292929', 'padding': '1rem', 'marginBottom': '0', 'marginTop': '0'},
        #                children='Click Dates in Box below to see Age distribution of Confirmed cases'),
        #        dcc.DatePickerRange(
        #                id='my-date-picker-range',
        #                min_date_allowed=datetime(2019, 12, 31),
        #                max_date_allowed=datetime(2022, 12, 31),
        #                initial_visible_month=datetime(2020, 1, 1),
        #                start_date=datetime(2020, 1, 1).date(),
        #                end_date=datetime(2020, 12, 31).date()
        #                ),
        #        dcc.Graph(
        #                id='histogram',
        #                style={'height':'500px'}
        #                )
        #            ]  ## children inside
        #        ) ### div  inside
        #        ]  ### children outside
        #    )  ###### div outside
        #        
        #            ######### End histogram plot
        ########### Plot end


       ### table
        html.Div(
            id='dcc-tabs',
            #style={'marginLeft': '1.5%', 'marginRight': '1.5%', 'marginBottom': '.5%'},
            style={'width': '95%', 'display': 'inline-block', 'verticalAlign': 'top',
                                     'box-shadow':'0px 0px 10px #ededee', 'border': '1px solid #ededee'},
                 children=[
                      html.H5(style={'textAlign': 'center', 'backgroundColor': '#ffffff',
                                                 'color': '#292929', 'padding': '1rem', 'marginBottom': '0', 'marginTop': '0'},
                                               children='Government Announcment'),
                                  dcc.Tabs(
                                        id="tabs-table",
                                        value='1-1',
                                        parent_className='custom-tabs',
                                        className='custom-tabs-container',
                                        children=[
                                             makePlot.make_dcc_table(dfLockdown),
                                             makePlot.make_dcc_table_2(dfAnn),
                                             makePlot.make_dcc_table_3(dfScr),

                                        ] ## inside children
                                  ) ## dcc tabs
                 ] ## children outside
            ) ## div outside
        ##### End table tabs
         
        ]), # Children outermost
        ##########################

]) # outter most


#@app.callback(
#    dash.dependencies.Output('histogram', 'figure'),
#    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
#     dash.dependencies.Input('my-date-picker-range', 'end_date')])
#def update_output(start_date, end_date):
#    #print(start_date,' :: ', type(start_date))
#    dfNew=prepData.GenerateNewTable(dfLoad_4,start_date,end_date)
#    fig2 = go.Figure(
#        go.Histogram( x=dfNew['Age'],
#         opacity=0.75,
#         #hisnorm='probability',
#         name='Age test'  )
#        )
#    fig2.update_layout(
#        #title='test age',
#        barmode='overlay',
#        xaxis=dict(
#            title='Age'
#            ),
#        yaxis=dict(
#            title='Frequency'
#            ),
#        )
#    return fig2




server = app.server

if __name__ == '__main__':
    #app.run_server(host="0.0.0.0", debug=True)
    app.run_server(debug=False)
