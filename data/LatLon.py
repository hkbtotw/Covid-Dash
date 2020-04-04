import pandas as pd
from googlemaps import Client as GoogleMaps

gmaps = GoogleMaps('AIzaSyCYA0c5qppFhpcGeWK-e1QIT6EBS3LoMx4')  # my account API, replace with yours

filename1=r'C:/Users/70018928/Documents/Project2020/coronavirus-py-master/corona-app-v1/Covid-Dash/data/prvDf.xlsx'
filename2=r'C:/Users/70018928/Documents/Project2020/coronavirus-py-master/corona-app-v1/Covid-Dash/data/Announcement_covid19_290363n.xlsx'

dfPrv=pd.read_excel(filename1)
dfAnn=pd.read_excel(filename2)

def LatLon_1(dfIn, colName):
    dfIn['lat'] = ""
    dfIn['lon'] = ""

    for x in range(len(dfIn)):
        dummy=dfIn[colName][x]
        if(dummy=='ไม่พบข้อมูล'):
            dummy='Thailand'

        geocode_result = gmaps.geocode(dummy)

        dfIn['lat'][x] = geocode_result[0]['geometry']['location']['lat']
        dfIn['lon'][x] = geocode_result[0]['geometry']['location']['lng']

    
    return dfIn

dfPrv=LatLon_1(dfPrv, 'PrvTh')
dfAnn=LatLon_1(dfAnn, 'Location')

fileout1=r'C:/Users/70018928/Documents/Project2020/coronavirus-py-master/corona-app-v1/Covid-Dash/data/prvDf_1.csv'
fileout2=r'C:/Users/70018928/Documents/Project2020/coronavirus-py-master/corona-app-v1/Covid-Dash/data/Announcement_covid19_290363n_1.csv'

dfPrv.to_csv(fileout1)
dfAnn.to_csv(fileout2)