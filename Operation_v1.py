import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np

monthDict={
    1:'Jan',
    2:'Feb',
    3:'Mar',
    4:'Apr',
    5:'May',
    6:'Jun',
    7:'Jul',
    8:'Aug',
    9:'Sep',
    10:'Oct',
    11:'Nov',
    12:'Dec'        
}

class PrepData(object):
    def __init__(self):
        self.datasetName1="https://covid19.th-stat.com/api/open/timeline"
        self.outbreakStart='12/31/2019'

    def LoadData(self):
        response = requests.get(self.datasetName1)
        #print(response.status_code)

        #print(response.json())
        result=response.json()

        #print(result,' == ',type(result))

        headerColumn=list(result.keys())
        #print(headerColumn)
        #print(result.values())

        updateDate=result['UpdateDate']
        headerData=list(result['Data'][0].keys())
        #print(headerData, ' === ',len(result['Data']))
        #print(result['Data'][90])

        dfData=pd.DataFrame(columns=['Date', 'NewConfirmed', 'NewRecovered', 'NewHospitalized', 'NewDeaths', 'Confirmed', 'Recovered', 'Hospitalized', 'Deaths','UpdateDate'])

        for n in range(len(result['Data'])):
            #print(n)
            newrow={'Date':result['Data'][n][headerData[0]], 'NewConfirmed':result['Data'][n][headerData[1]], 'NewRecovered':result['Data'][n][headerData[2]], 
               'NewHospitalized':result['Data'][n][headerData[3]], 'NewDeaths':result['Data'][n][headerData[4]], 'Confirmed':result['Data'][n][headerData[5]],
                'Recovered':result['Data'][n][headerData[6]], 'Hospitalized':result['Data'][n][headerData[7]], 'Deaths':result['Data'][n][headerData[8]],'UpdateDate':updateDate}
            dfData=dfData.append(newrow, ignore_index=True)
        
        dfData['Active']=dfData['Confirmed']-dfData['Recovered']-dfData['Deaths']

        deathsList=dfData['Deaths'].values.tolist()
        confirmedList=dfData['Confirmed'].values.tolist()
        deathrateList=[]
        for n in range(len(dfData)):
            if(confirmedList[n]==0):
                deathrateList.append(0)
            else:
                deathrateList.append(deathsList[n]/confirmedList[n])
        dfDeathrate=pd.DataFrame(deathrateList)
        dfDeathrate.columns=['DeathRate']
        dfData=pd.concat([dfData,dfDeathrate],axis=1)
        #dfData['DeathRate']=dfData['Deaths']/dfData['Confirmed']
        return dfData
    
    def NumberPlateCalculation(self, dfLoad):

        def PercentageCalc(valNew, valOld):
            return (valNew-valOld)/valOld
        
        maxDate=max(dfLoad['Date'])
        mn1Date=(datetime.strptime(maxDate, '%m/%d/%Y') - timedelta(days=1)).strftime("%m/%d/%Y")

        daysOutbreak=(datetime.strptime(maxDate, '%m/%d/%Y')-datetime.strptime(self.outbreakStart, '%m/%d/%Y')).days
        #print(' daysOutbreak : ',daysOutbreak)
        Confirmed=list(dfLoad[dfLoad['Date']==maxDate]['Confirmed'])[0]
        mn1Confirmed=list(dfLoad[dfLoad['Date']==mn1Date]['Confirmed'])[0]
        pConfirmed=PercentageCalc(Confirmed,mn1Confirmed)

        Recovered=list(dfLoad[dfLoad['Date']==maxDate]['Recovered'])[0]
        mn1Recovered=list(dfLoad[dfLoad['Date']==mn1Date]['Recovered'])[0]
        pRecovered=PercentageCalc(Recovered,mn1Recovered)

        Deaths=list(dfLoad[dfLoad['Date']==maxDate]['Deaths'])[0]
        mn1Deaths=list(dfLoad[dfLoad['Date']==mn1Date]['Deaths'])[0]
        pDeaths=PercentageCalc(Deaths,mn1Deaths)

        newConfirmed=list(dfLoad[dfLoad['Date']==maxDate]['NewConfirmed'])[0]
        if(newConfirmed>=0):
            newCsym='+'
        else:
            newCsym='-'
        newRecovered=list(dfLoad[dfLoad['Date']==maxDate]['NewRecovered'])[0]
        if(newRecovered>=0):
            newRsym='+'
        else:
            newRsym='-'
        newDeaths=list(dfLoad[dfLoad['Date']==maxDate]['NewDeaths'])[0]
        if(newDeaths>=0):
            newDsym='+'
        else:
            newDsym='-'
        print(' > ',Confirmed,' :: ',Recovered,' :: ',Deaths)
        print(' > ',newConfirmed,' :: ',newRecovered,' :: ',newDeaths)
        return pConfirmed, pRecovered, pDeaths, daysOutbreak,maxDate,Confirmed, Recovered, Deaths, newConfirmed, newCsym, newRecovered, newRsym, newDeaths, newDsym


class MakePlot(object):
    def ConvertDate(self,test):
        day=test[3:5]
        month=monthDict[int(test[0:2])]
        year=(test[len(test)-4:len(test)])
        return month+' '+day+' '+year

    def ConvertDate_StringToDatetime(self,test):
        return datetime.strptime(test, '%m/%d/%Y')

    def ProgressUpdatePlot(self, dfIn):
        
        # Convert String Date to Datetime Date
        dfPlot=dfIn.copy()
        newdateCol=[ self.ConvertDate_StringToDatetime(d)  for d in dfIn['Date']]
        dfnewdateCol=pd.DataFrame(newdateCol)
        dfnewdateCol.columns=['newDate']
        dfPlot=pd.concat([dfPlot,dfnewdateCol],axis=1)

        ###################  fig confirmed
        # Create empty figure canvas
        fig_confirmed = go.Figure()
        # Add trace to the figure
        fig_confirmed.add_trace(go.Scatter(x=dfPlot['newDate'], y=dfPlot['Confirmed'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Thailand',
                                   line=dict(color='#921113', width=4),
                                   marker=dict(size=4, color='#f4f4f2',
                                               line=dict(width=1, color='#921113')),
                                   text=[datetime.strftime(
                                       d, '%b %d %Y AEDT') for d in dfPlot['newDate']],
                                   hovertext=['Confirmed<br>{:,d} cases<br>'.format(
                                       i) for i in dfIn['Confirmed']],
                                   hovertemplate='<b>%{text}</b><br></br>' +
                                                 '%{hovertext}' +
                                                 '<extra></extra>'))
        
        # Customise layout
        fig_confirmed.update_layout(
        #    title=dict(
        #    text="<b>Confirmed Cases Timeline<b>",
        #    y=0.96, x=0.5, xanchor='center', yanchor='top',
        #    font=dict(size=20, color="#292929", family="Playfair Display")
        #   ),
            margin=go.layout.Margin(
                l=10,
                r=10,
                b=10,
                t=5,
                pad=0
            ),
            yaxis=dict(
                showline=False, linecolor='#272e3e',
                zeroline=False,
                # showgrid=False,
                gridcolor='rgba(203, 210, 211,.3)',
                gridwidth=.1,
            #tickmode='array',
            # Set tick range based on the maximum number
            #tickvals=tickList,
            # Set tick label accordingly
            #ticktext=["{:.0f}k".format(i/1000) for i in tickList]
            ),
            #   yaxis_title="Total Confirmed Case Number",
            xaxis=dict(
                showline=False, linecolor='#272e3e',
                showgrid=False,
                gridcolor='rgba(203, 210, 211,.3)',
                gridwidth=.1,
                zeroline=False
            ),
            xaxis_tickformat='%b %d',
            hovermode='x',
            legend_orientation="h",
            #   legend=dict(x=.02, y=.95, bgcolor="rgba(0,0,0,0)",),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(color='#292929', size=10)
            )  # Layout
        ############## figcombined
        # Create empty figure canvas
        fig_combine = go.Figure()
        # Add trace to the figure
        fig_combine.add_trace(go.Scatter(x=dfPlot['newDate'], y=dfPlot['Recovered'],
                                   mode='lines+markers',
                                   line_shape='spline',
                                   name='Total Recovered Cases',
                                   line=dict(color='#168038', width=4),
                                   marker=dict(size=4, color='#f4f4f2',
                                               line=dict(width=1, color='#168038')),
                                   text=[datetime.strftime(
                                       d, '%b %d %Y AEDT') for d in dfPlot['newDate']],
                                   hovertext=['Total recovered<br>{:,d} cases<br>'.format(
                                       i) for i in dfPlot['Recovered']],
                                   hovertemplate='<b>%{text}</b><br></br>' +
                                                 '%{hovertext}' +
                                                 '<extra></extra>'))
        fig_combine.add_trace(go.Scatter(x=dfPlot['newDate'], y=dfPlot['Deaths'],
                                mode='lines+markers',
                                line_shape='spline',
                                name='Total Death Cases',
                                line=dict(color='#626262', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#626262')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in dfPlot['newDate']],
                                hovertext=['Total death<br>{:,d} cases<br>'.format(
                                    i) for i in dfPlot['Deaths']],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))
        fig_combine.add_trace(go.Scatter(x=dfPlot['newDate'], y=dfPlot['Active'],
                                mode='lines+markers',
                                line_shape='spline',
                                name='Total Active Cases',
                                line=dict(color='#e36209', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#e36209')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in dfPlot['newDate']],
                                hovertext=['Total active<br>{:,d} cases<br>'.format(
                                    i) for i in dfPlot['Active']],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))
        # Customise layout
        fig_combine.update_layout(
            margin=go.layout.Margin(
            l=10,
            r=10,
            b=10,
            t=5,
            pad=0
            ),
            yaxis=dict(
            showline=False, linecolor='#272e3e',
            zeroline=False,
            # showgrid=False,
            gridcolor='rgba(203, 210, 211,.3)',
            gridwidth=.1,
            #tickmode='array',
            # Set tick range based on the maximum number
            #tickvals=tickList,
            # Set tick label accordingly
            #ticktext=["{:.0f}k".format(i/1000) for i in tickList]
            ),
            #       yaxis_title="Total Confirmed Case Number",
            xaxis=dict(
            showline=False, linecolor='#272e3e',
            showgrid=False,
            gridcolor='rgba(203, 210, 211,.3)',
            gridwidth=.1,
            zeroline=False
            ),
            xaxis_tickformat='%b %d',
            hovermode='x',
            legend_orientation="h",
            # legend=dict(x=.02, y=.95, bgcolor="rgba(0,0,0,0)",),
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(color='#292929', size=10)
            )
        ############## fig_deathrate

        # Line plot for death rate cases
        # Set up tick scale based on death case number of Mainland China
        tickList = np.arange(0, (dfPlot['DeathRate']*100).max()+0.5, 0.5)

        # Create empty figure canvas
        fig_rate = go.Figure()
        # Add trace to the figure
        fig_rate.add_trace(go.Scatter(x=dfPlot['newDate'], y=dfPlot['DeathRate']*100,
                                mode='lines+markers',
                                line_shape='spline',
                                name='Thailand',
                                line=dict(color='#626262', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#626262')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in dfPlot['newDate']],
                                hovertext=['Thailand death rate<br>{:.2f}%'.format(
                                    i) for i in dfPlot['DeathRate']*100],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))
        # Customise layout
        fig_rate.update_layout(
            margin=go.layout.Margin(
            l=10,
            r=10,
            b=10,
            t=5,
            pad=0
            ),
            yaxis=dict(
                showline=False, linecolor='#272e3e',
                zeroline=False,
                # showgrid=False,
                gridcolor='rgba(203, 210, 211,.3)',
                gridwidth=.1,
                tickmode='array',
                # Set tick range based on the maximum number
                tickvals=tickList,
                # Set tick label accordingly
                ticktext=['{:.1f}'.format(i) for i in tickList]
                ),
            #    yaxis_title="Total Confirmed Case Number",
            xaxis=dict(
                showline=False, linecolor='#272e3e',
                showgrid=False,
                gridcolor='rgba(203, 210, 211,.3)',
                gridwidth=.1,
                zeroline=False
                ),
            xaxis_tickformat='%b %d',
                hovermode='x',
                legend_orientation="h",
                # legend=dict(x=.02, y=.95, bgcolor="rgba(0,0,0,0)",),
                plot_bgcolor='#ffffff',
                paper_bgcolor='#ffffff',
                font=dict(color='#292929', size=10)
                )               




        
        return fig_confirmed, fig_combine, fig_rate


