import pandas as pd
from datetime import datetime
import time 
import requests
import os
import hopsworks

from features import *


AIR_QUALITY_API_KEY = os.getenv('AIR_QUALITY_API_KEY')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')

date_today = datetime.now().strftime("%Y-%m-%d")


cities = ['Kyiv','Stockholm','Sundsvall','Malmo']

data_air_quality = [get_air_quality_data(city,AIR_QUALITY_API_KEY) for city in cities]
data_weather = [get_weather_data(city,date_today,WEATHER_API_KEY) for city in cities]


df_air_quality = get_air_quality_df(data_air_quality)
df_air_quality.aqi = df_air_quality.aqi.replace('-',24)


df_weather = get_weather_df(data_weather)


project = hopsworks.login()

fs = project.get_feature_store() 


air_quality_fg = fs.get_or_create_feature_group(
    name = 'air_quality_fg',
    version = 1
)
weather_fg = fs.get_or_create_feature_group(
    name = 'weather_fg',
    version = 1
)


index_latest = air_quality_fg.read()['index'].max()

prepare_index(df_air_quality,index_latest)
prepare_index(df_weather,index_latest)



air_quality_fg.insert(df_air_quality)
weather_fg.insert(df_weather)
