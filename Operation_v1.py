import os
import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import numpy as np
from googlemaps import Client as GoogleMaps
import math

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
        self.datasetName2="https://covid19.th-stat.com/api/open/cases/sum"
        self.datasetName3="https://covid19.th-stat.com/api/open/cases"
        self.outbreakStart='12/31/2019'

    def LoadData_Timeline(self):
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

        confirmedChange=[]
        for n in range(len(dfData)):
            if(n==0):
                confirmedChange.append(0)
            else:
                if(confirmedList[n-1]==0):
                    confirmedChange.append(0)
                else:
                    confirmedChange.append((confirmedList[n]-confirmedList[n-1])/confirmedList[n-1])
        dfConfirmedChange=pd.DataFrame(confirmedChange)
        dfConfirmedChange.columns=['ConfirmedChange']
        dfData=pd.concat([dfData,dfDeathrate,dfConfirmedChange],axis=1)

        #fileout=r'C:/Users/70018928/Documents/Project2020/coronavirus-py-master/out_check.csv'
        #dfData.to_csv(fileout)

        return dfData
    
    def LoadData_Casesum(self):
        response = requests.get(self.datasetName2)
        #print(response.status_code)

        result=response.json()

        headerColumn=list(result.keys())
        dfData=pd.DataFrame(columns=['Category','Attribute','Value'])
        header1=list(result['Province'])

        for n in header1:
            #print(n)
            newrow={'Category':'Province', 'Attribute':n, 'Value':result['Province'][n]}
            dfData=dfData.append(newrow, ignore_index=True)

        header1=list(result['Nation'])
        #print(header1)
        for n in header1:
            #print(n)
            newrow={'Category':'Nation', 'Attribute':n, 'Value':result['Nation'][n]}
            dfData=dfData.append(newrow, ignore_index=True)

        header1=list(result['Gender'])
        #print(header1)
        for n in header1:
            #print(n)
            newrow={'Category':'Gender', 'Attribute':n, 'Value':result['Gender'][n]}
            dfData=dfData.append(newrow, ignore_index=True)

        return dfData

    def LoadData_CaseDesc(self):
        response = requests.get(self.datasetName3)
        #print(response.status_code)

        result=response.json()

        #print(result,' == ',type(result))

        headerColumn=list(result.keys())

        header1=list(result['Data'][0].keys())

        dfData=pd.DataFrame(columns=['ConfirmDate', 'No', 'Age', 'Gender', 'GenderEn', 'Nation', 'NationEn', 'Province', 'ProvinceId', 'ProvinceEn'])

        for n in range(len(result['Data'])):
            #print(n)
            newrow={'ConfirmDate':result['Data'][n][header1[0]], 'No':result['Data'][n][header1[1]], 'Age':result['Data'][n][header1[2]], 
            'Gender':result['Data'][n][header1[3]], 'GenderEn':result['Data'][n][header1[4]], 'Nation':result['Data'][n][header1[5]],
            'NationEn':result['Data'][n][header1[6]], 'Province':result['Data'][n][header1[7]], 'ProvinceId':result['Data'][n][header1[8]],
            'ProvinceEn':result['Data'][n][header1[10]]}
            dfData=dfData.append(newrow, ignore_index=True)

        #print(dfData)

        # Create Dict of Province List to use in Location search in map api
        provincethList=list(set(dfData['Province'].values.tolist()))
        provinceEnList=[]
        for n in provincethList:
            provinceEnList.append(list(set(list(dfData[dfData['Province']==n]['ProvinceEn'])))[0])

        prvDict=dict(zip(provinceEnList, provincethList))

        return dfData, prvDict

    def Load_prvDict(self):
        #filein=r'C:/Users/70018928/Documents/Project2020/coronavirus-py-master/corona-app-v1/Covid-Dash/prvDf.xlsx'
        filename=os.listdir('./data/')
        print(' filename : ',filename)
        dfPrv=pd.read_excel(filename[0])
        
        #dfPrv=pd.read_excel(filein)
        thList=dfPrv['PrvTh'].values.tolist()
        #print(thList)
        enList=dfPrv['PrvEn'].values.tolist()
        #print(enList)
        

#        thList=['อ่างทอง', 'อำนาจเจริญ', 'กรุงเทพมหานคร', 'บึงกาฬ', 'บุรีรัมย์', 'ฉะเชิงเทรา', 'ชัยนาท', 'ชัยภูมิ', 'จันทบุรี', 'เชียงใหม่', 
#        'เชียงราย', 'ชลบุรี', 'ชุมพร', 'กาฬสินธุ์', 'กาญจนบุรี', 'ขอนแก่น', 'กระบี่', 'ลำพูน', 'เลย', 'ลพบุรี', 'แม่ฮ่องสอน', 'มหาสารคาม',
#         'มุกดาหาร', 'นครนายก', 'นครปฐม', 'นครพนม', 'นครราชสีมา', 'นครสวรรค์', 'นครศรีธรรมราช', 'น่าน', 'นราธิวาส', 'หนองบัวลำภู', 'หนองคาย',
#          'นนทบุรี', 'ประเทศไทย', 'ปทุมธานี', 'ปัตตานี', 'พังงา', 'พัทลุง', 'พะเยา', 'เพชรบูรณ์', 'เพชรบุรี', 'พิจิตร', 'พิษณุโลก', 'อยุธยา',
#           'แพร่', 'ภูเก็ต', 'ปราจีนบุรี', 'ประจวบคีรีขันธ์', 'ระนอง', 'ราชบุรี', 'ระยอง', 'ร้อยเอ็ด', 'สระแก้ว', 'สกลนคร', 'สมุทรปราการ', 'สมุทรสาคร',
#            'สมุทรสงคราม', 'สระบุรี', 'สตูล', 'สิงห์บุรี', 'ศรีสะเกษ', 'สงขลา', 'สุโขทัย', 'สุพรรณบุรี', 'สุราษฎร์ธานี', 'สุรินทร์', 'ตาก',
#             'ตราด', 'ตรัง', 'อุบลราชธานี', 'อุดรธานี', 'ไม่พบข้อมูล', 'อุทัยธานี', 'อุตรดิตถ์', 'ยะลา', 'ยโสธร']
#        enList=['Ang Thong', 'Amnat Charoen', 'Bangkok', 'Bueng Kan', 'Buriram', 'Chachoengsao', 'Chai Nat', 'Chaiyaphum', 'Chanthaburi', 'Chiang Mai', 'Chiang Rai', 'Chonburi', 'Chumphon', 'Kalasin', 'Kanchanaburi', 'Khon Kaen', 'Krabi', 'Lamphun', 'Loei', 'Lopburi',
#         'Mae Hong Son', 'Maha Sarakham', 'Mukdahan', 'Nakhon Nayok', 'Nakhon Pathom', 'Nakhon Phanom', 'Nakhon Ratchasima', 'Nakhon Sawan', 'Nakhon Si Thammarat', 'Nan', 'Narathiwat', 'Nong Bua Lamphu', 'Nong Khai', 'Nonthaburi', 'Northeast', 'Pathum Thani', 'Pattani',
#          'Phang Nga', 'Phatthalung', 'Phayao', 'Phetchabun', 'Phetchaburi', 'Phichit', 'Phitsanulok',
#          'Phra Nakhon Si Ayutthaya', 'Phrae', 'Phuket', 'Prachinburi', 'Prachuap Khiri Khan', 'Ranong', 'Ratchaburi', 
#         'Rayong', 'Roi Et', 'Sa Kaeo', 'Sakon Nakhon', 'Samut Prakan', 'Samut Sakhon', 'Samut Songkhram', 'Saraburi',
#         'Satun', 'Sing Buri', 'Sisaket', 'Songkhla', 'Sukhothai', 'Suphan Buri', 'Surat Thani', 'Surin', 'Tak', 'Trat',
#          'Trang', 'Ubon Ratchathani', 'Udon Thani', 'Unknown', 'Uthai Thani', 'Uttaradit', 'Yala', 'Yasothon']      
        
        print(len(thList), ' :: ',len(enList))

        prvDict=dict(zip(enList,thList))

        return prvDict

    def CalcTrendTable(self,dfIn):
        dfOut=dfIn[dfIn['Confirmed']>=100].copy().reset_index()
        dayList=np.arange(1, len(dfOut)+1)
        dfdayList=pd.DataFrame(dayList)
        dfdayList.columns=['DayElapsed']
        dfOut=pd.concat([dfOut,dfdayList],axis=1)

        return dfOut

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
    def __init__(self):
        self.mapbox_access_token="pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
        self.gmaps = GoogleMaps('AIzaSyCYA0c5qppFhpcGeWK-e1QIT6EBS3LoMx4')  # my account API, replace with yours

    def LatLon_Province(self, dfIn, prvDict):
        dfData=dfIn[dfIn['Category']=='Province'].copy().reset_index()

        dfData['lat'] = ""
        dfData['lon'] = ""

        for x in range(len(dfData)):
            dummy=prvDict[dfData['Attribute'][x]]
            #print(dfData['Attribute'][x], ' ::  ',dummy)
            #print('1 :  ',dfData['Province'][x])
            if(dummy=='ไม่พบข้อมูล'):
                dummy='Thailand'
            #print(' 2   : ',dfData['Province'][x])
            geocode_result = self.gmaps.geocode(dummy)

            #print(dfData['Attribute'][x], '  :::    ',geocode_result[0]['geometry'])
            #print(dfData['Attribute'][x],'  ===>    ',geocode_result[0]['geometry']['location'])
            dfData['lat'][x] = geocode_result[0]['geometry']['location'] ['lat']
            dfData['lon'][x] = geocode_result[0]['geometry']['location']['lng']

            #latList=dfIn['lat'].values.tolist()
            #longList=dfIn['long'].values.tolist()
            #pairList=list(zip(latList,longList))

        #print(dfData)
        return dfData

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
        ######## fig_confirmedChange

        # Line plot for death rate cases
        # Set up tick scale based on death case number of Mainland China
        tickList = np.arange(0, (dfPlot['ConfirmedChange']*100).max()+0.5, 0.5)

        # Create empty figure canvas
        fig_confirmedChange = go.Figure()
        # Add trace to the figure
        fig_confirmedChange.add_trace(go.Scatter(x=dfPlot['newDate'], y=dfPlot['ConfirmedChange']*100,
                                mode='lines+markers',
                                line_shape='spline',
                                name='Thailand',
                                line=dict(color='#921113', width=4),
                                marker=dict(size=4, color='#f4f4f2',
                                            line=dict(width=1, color='#626262')),
                                text=[datetime.strftime(
                                    d, '%b %d %Y AEDT') for d in dfPlot['newDate']],
                                hovertext=['Thailand %Change of Confirmed case daily<br>{:.2f}%'.format(
                                    i) for i in dfPlot['ConfirmedChange']*100],
                                hovertemplate='<b>%{text}</b><br></br>' +
                                              '%{hovertext}' +
                                              '<extra></extra>'))
        # Customise layout
        fig_confirmedChange.update_layout(
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
                #ticktext=['{:.1f}'.format(i) for i in tickList]
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
               
        
        return fig_confirmed, fig_combine, fig_rate, fig_confirmedChange

    def TrendPlot(self,dfIn,daysOutbreak):
        # Pseduo data for logplot
        pseduoDay = np.arange(1, daysOutbreak+1)
        y1 = 100*(1.85)**(pseduoDay-1)  # 85% growth rate
        y2 = 100*(1.35)**(pseduoDay-1)  # 35% growth rate
        y3 = 100*(1.15)**(pseduoDay-1)  # 15% growth rate
        y4 = 100*(1.05)**(pseduoDay-1)  # 5% growth rate

        # Default curve plot for tab
        # Create   empty figure canvas
        fig_curve_tab = go.Figure()

        fig_curve_tab.add_trace(go.Scatter(x=pseduoDay,
                                   y=y1,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=['85% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
                    )
        fig_curve_tab.add_trace(go.Scatter(x=pseduoDay,
                                   y=y2,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=['35% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
                    )
        fig_curve_tab.add_trace(go.Scatter(x=pseduoDay,
                                   y=y3,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=['15% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
                    )
        fig_curve_tab.add_trace(go.Scatter(x=pseduoDay,
                                   y=y4,
                                   line=dict(color='rgba(0, 0, 0, .3)', width=1, dash='dot'),
                                   text=['5% growth rate' for i in pseduoDay],
                                   hovertemplate='<b>%{text}</b><br>' +
                                                 '<extra></extra>'
                            )
                    )
        

        dotgrayx_tab = np.array(dfIn['DayElapsed'])
        dotgrayy_tab = np.array(dfIn['Confirmed'])

        fig_curve_tab.add_trace(go.Scatter(x=dfIn['DayElapsed'],
                                     y=dfIn['Confirmed'],
                                     mode='lines',
                                     line_shape='spline',
                                     name='Thailand',
                                     opacity=0.3,
                                     line=dict(color='#921113', width=1.5),
                                     text=['Thailand' for i in dfIn['DayElapsed']],
                                     hovertemplate='<b>%{text}</b><br>' +
                                                   '<br>%{x} days after 100 cases<br>' +
                                                   'with %{y:,d} cases<br>'
                                                   '<extra></extra>'
                             )
                    )

        fig_curve_tab.add_trace(go.Scatter(x=dotgrayx_tab,
                                     y=dotgrayy_tab,
                                     mode='markers',
                                     marker=dict(size=6, color='#636363',
                                     line=dict(width=1, color='#636363')),
                                     opacity=0.5,
                                     text=['Thailand' for i in dotgrayx_tab],
                                     hovertemplate='<b>%{text}</b><br>' +
                                                   '<br>%{x} days after 100 cases<br>' +
                                                   'with %{y:,d} cases<br>'
                                                   '<extra></extra>'
                            )
                    )

        # Customise layout
        fig_curve_tab.update_xaxes(range=[0, len(dfIn)+30])
        fig_curve_tab.update_yaxes(range=[1.9, 7])
        fig_curve_tab.update_layout(
                xaxis_title="Number of day since 100th confirmed cases",
                yaxis_title="Confirmed cases (Logarithmic)",
                margin=go.layout.Margin(
                        l=10,
                        r=10,
                        b=10,
                        t=5,
                        pad=0
                    ),
             #annotations=[dict(
            #    x=.5,
            #    y=.4,
            #    xref="paper",
            #    yref="paper",
            #    text=dfSum['Country/Region'][0] if dfSum['Country/Region'][0] in set(dfs_curve['Region']) else "Not over 100 cases",
            #    opacity=0.5,
            #    font=dict(family='Arial, sans-serif',
            #              size=60,
            #              color="grey"),
            #            )
            #],
            yaxis_type="log",
            yaxis=dict(
                showline=False, 
                linecolor='#272e3e',
                zeroline=False,
                # showgrid=False,
                gridcolor='rgba(203, 210, 211,.3)',
                gridwidth = .1,
            ),
            xaxis=dict(
               showline=False, 
                linecolor='#272e3e',
                # showgrid=False,
                gridcolor='rgba(203, 210, 211,.3)',
                gridwidth = .1,
                zeroline=False
            ),
            showlegend=False,
                # hovermode = 'x',
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            font=dict(color='#292929', size=10)
            )



        return fig_curve_tab

    def MapPlot(self,dfIn):
        
        latitude = 13.736717
        longitude = 100.523186 
        zoom = 4 
        hovertext_value = ['Confirmed: {:,d}<br>'.format(i) for i in dfIn['Value']]

        colorList=dfIn['Value'].values.tolist()
        textList=dfIn['Attribute'].values.tolist()
        
        fig2 = go.Figure(go.Scattermapbox(
            lat=dfIn['lat'],
            lon=dfIn['lon'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                color=['#d7191c' if i > 0 else '#1a9622' for i in colorList],
                size=[i**(1/3) for i in dfIn['Value']],
                sizemin=1,
                sizemode='area',
                sizeref=2.*max([math.sqrt(i)
                           for i in dfIn['Value']])/(100.**2),
                ),
            text=textList,
            hovertext=hovertext_value,
            hovertemplate="<b>%{text}</b><br><br>" +
                        "%{hovertext}<br>" +
                        "<extra></extra>")
            )
        fig2.update_layout(
            plot_bgcolor='#ffffff',
            paper_bgcolor='#ffffff',
            margin=go.layout.Margin(l=10, r=10, b=10, t=0, pad=40),
            hovermode='closest',
            transition={'duration': 50},
            annotations=[
            dict(
                x=.5,
                y=-.0,
                align='center',
                showarrow=False,
                text="Points are placed based on data geolocation levels.<br>Province/State level - Australia, China, Canada, and United States; Country level- other countries.",
                xref="paper",
                yref="paper",
                font=dict(size=10, color='#292929'),
            )],
        mapbox=go.layout.Mapbox(
            accesstoken=self.mapbox_access_token,
            style="light",
            # The direction you're facing, measured clockwise as an angle from true north on a compass
            bearing=0,
            center=go.layout.mapbox.Center(
                lat=latitude,
                lon=longitude
            ),
            pitch=0,
            zoom=zoom
             )
        )     
        return fig2