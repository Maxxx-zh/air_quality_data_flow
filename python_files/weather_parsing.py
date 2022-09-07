import pandas as pd
from datetime import datetime
import time 
import requests
import os
import hopsworks



API_KEY = API_KEY = os.getenv('WEATHER_API_KEY')

date_today = datetime.now().strftime("%Y-%m-%d")


def get_json(city, date, API_KEY=API_KEY):
    return requests.get(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{city.lower()}/{date}?unitGroup=metric&include=days&key={API_KEY}&contentType=json').json()


def get_data(city_name,date=date_today):
    json = get_json(city_name,date)
    data = json['days'][0]
    
    return [
        json['address'],
        [json['latitude'],json['longitude']],
        data['datetime'],
        data['tempmax'],
        data['tempmin'],
        data['temp'],
        data['feelslikemax'],
        data['feelslikemin'],
        data['feelslike'],
        data['dew'],
        data['humidity'],
        data['precip'],
        data['precipprob'],
        data['precipcover'],
        data['snow'],
        data['snowdepth'],
        data['windgust'],
        data['windspeed'],
        data['winddir'],
        data['pressure'],
        data['cloudcover'],
        data['visibility'],
        data['solarradiation'],
        data['solarenergy'],
        data['uvindex'],
        data['conditions']
    ]


def timestamp_2_time(x):
    dt_obj = datetime.strptime(str(x), '%Y-%m-%d')
    dt_obj = dt_obj.timestamp() * 1000
    return int(dt_obj)


cities = ['Kyiv','Stockholm','Sundsvall','Malmo']

data_parsed = [get_data(city) for city in cities]


col_names = [
    'city',
    'location',
    'date',
    'tempmax',
    'tempmin',
    'temp',
    'feelslikemax',
    'feelslikemin',
    'feelslike',
    'dew',
    'humidity',
    'precip',
    'precipprob',
    'precipcover',
    'snow',
    'snowdepth',
    'windgust',
    'windspeed',  
    'winddir',
    'pressure',
    'cloudcover', 
    'visibility',
    'solarradiation',
    'solarenergy',
    'uvindex',
    'conditions'
]



new_data = pd.DataFrame(
    data_parsed,
    columns=col_names
)
new_data.date = new_data.date.apply(timestamp_2_time)



project = hopsworks.login()

fs = project.get_feature_store() 


def get_or_create_feature_group(name='weather_fg',fs=fs):
    feature_group = fs.get_or_create_feature_group(
        name=name,
        description = 'Characteristics of each day',
        version = 1,
        primary_key = ['index'],
        online_enabled = True,
        event_time = ['date']
    )
    return feature_group


feature_group = get_or_create_feature_group()

feature_group.insert(new_data.reset_index())

