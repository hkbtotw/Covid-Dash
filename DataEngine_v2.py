from hdx.hdx_configuration import Configuration 
from hdx.data.dataset import Dataset
import pandas as pd


baseURL = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/"


def loadData(fileName, columnName): 
    data = pd.read_csv(baseURL + fileName) \
             .drop(['Lat', 'Long'], axis=1) \
             .melt(id_vars=['Province/State', 'Country/Region'], var_name='date', value_name=columnName) \
             .astype({'date':'datetime64[ns]', columnName:'Int64'}, errors='ignore')
    data['Province/State'].fillna('<all>', inplace=True)
    data[columnName].fillna(0, inplace=True)
    return data


class DataPrep(object):
    def __init__(self):
        self.datasetName='novel-coronavirus-2019-ncov-cases' 

    def ConfigLoadData(self):
        Configuration.create(hdx_site='prod', user_agent='A_Quick_Example', hdx_read_only=True)
        return Dataset.read_from_hdx(self.datasetName)

    def LoadData(self,dataset,resourceId):
        # name of the dataset, see above
        resources = dataset.get_resources()
    
        # resource id (e.g., resource[id]) comes from the number of the dataset you see on the dataset page
        # e.g., on this page id=0 is time_series_covid19_confirmed_global.csv
        url, path = resources[resourceId].download()
        
        return pd.read_csv(path)