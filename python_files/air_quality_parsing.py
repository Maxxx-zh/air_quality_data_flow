import hopsworks
import requests
from datetime import datetime
import os
import pandas as pd


API_KEY = os.getenv('AIR_QUALITY_API_KEY')


def get_json(city_name):
    return requests.get(f'https://api.waqi.info/feed/{city_name}/?token={API_KEY}').json()['data']


def get_data(city_name):
    json = get_json(city_name)
    iaqi = json['iaqi']
    forecast = json['forecast']['daily']
    return [
        city_name,
        json['aqi'],                 # AQI 
        json['time']['s'],           # Date
        str(json['city']['geo']),    # Location
        iaqi['h']['v'],
        iaqi['p']['v'],
        iaqi['pm10']['v'],
        iaqi['t']['v'],
        forecast['o3'][0]['avg'],
        forecast['o3'][0]['max'],
        forecast['o3'][0]['min'],
        forecast['pm10'][0]['avg'],
        forecast['pm10'][0]['max'],
        forecast['pm10'][0]['min'],
        forecast['pm25'][0]['avg'],
        forecast['pm25'][0]['max'],
        forecast['pm25'][0]['min'],
        forecast['uvi'][0]['avg'],
        forecast['uvi'][0]['avg'],
        forecast['uvi'][0]['avg']
    ]


def timestamp_2_time(x):
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d %H:%M:%S')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)



cities = ['Kyiv','Lviv','Stockholm','Sundsvall','Malmo']

data_parsed = [get_data(city) for city in cities]


col_names = [
    'city',
    'aqi',
    'date',
    'location',
    'iaqi_h',
    'iaqi_p',
    'iaqi_pm10',
    'iaqi_t',
    'o3_avg',
    'o3_max',
    'o3_min',
    'pm10_avg',
    'pm10_max',
    'pm10_min',
    'pm25_avg',
    'pm25_max',
    'pm25_min',  
    'uvi_avg',
    'uvi_max',
    'uvi_min', 
]


new_data = pd.DataFrame(
    data_parsed,
    columns=col_names
)
new_data.date = new_data.date.apply(timestamp_2_time)

new_data.head()


project = hopsworks.login()

fs = project.get_feature_store() 


def retrieve_feature_group(name='air_quality',fs=fs):
    feature_group = fs.get_feature_group(
        name=name,
        version=1
    )
    return feature_group

def create_feature_group(data,name='air_quality',fs=fs):
    
    feature_group = fs.get_or_create_feature_group(
        name=name,
        description = 'Characteristics of each day',
        version = 1,
        primary_key = ['index'],
        online_enabled = True,
        event_time = ['date']
    )
        
    feature_group.insert(data.reset_index())
    
    return feature_group



try:
    feature_group = retrieve_feature_group()
    feature_group.insert(new_data.reset_index())
    
except:
    feature_group = create_feature_group(new_data)
