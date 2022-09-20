import streamlit as st
import hopsworks
import joblib
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium, folium_static
import json
import time
from branca.element import Figure

st.title('⛅️Air Quality Prediction Project🌩')


progress_bar = st.sidebar.header('⚙️ Working Progress')
progress_bar = st.sidebar.progress(0)
st.write(36 * "-")
st.subheader('\n📡 Connecting to Hopsworks Feature Store...')

project = hopsworks.login()
fs = project.get_feature_store()

st.write("Successfully connected!✔️")
progress_bar.progress(20)

st.write(36 * "-")
st.subheader('\n☁️ Getting data from Feature Store...')


@st.cache(suppress_st_warning=True)
def get_recent_data():
    feature_view = fs.get_feature_view(name="air_quality_fv")
    res = feature_view.query.read().sort_values(by=["date", 'city']).head(4)
    return res


recent_weather_data = get_recent_data()


latest_date_unix = str(recent_weather_data.date.values[0])[:10]

import time
latest_date = time.ctime(int(latest_date_unix))

st.write(36 * "-")
st.subheader(f"Data for {latest_date}")

progress_bar.progress(30)

# train_data = feature_view.get_training_data(1)[0]
# train_data.sort_values(by=["date", 'city']).head(4)


# st.sidebar.write(recent_data[["city", "aqi"]])
st.write(36 * "-")
st.subheader(f"🗺 Processing the map...")

recent_weather_data = recent_weather_data[["city", "temp", "humidity",
                                            "conditions", "aqi"]]
recent_weather_data = recent_weather_data.set_index("city")

cols_names_dict = {"temp": "Temperature",
                   "humidity": "Humidity",
                   "conditions": "Conditions",
                   "aqi": "Air Quality Index"}

recent_weather_data = recent_weather_data.rename(columns=cols_names_dict)
progress_bar.progress(40)
#
#     st.subheader('\n🎉 📈 🤝 App Finished Successfully 🤝 📈 🎉')


fig = Figure(width=550,height=350)

my_map = folium.Map(location=[56, 20], zoom_start=3.71)
fig.add_child(my_map)
folium.TileLayer('Stamen Terrain').add_to(my_map)
folium.TileLayer('Stamen Toner').add_to(my_map)
folium.TileLayer('Stamen Water Color').add_to(my_map)
folium.TileLayer('cartodbpositron').add_to(my_map)
folium.TileLayer('cartodbdark_matter').add_to(my_map)
folium.LayerControl().add_to(my_map)


cities_coords = {("Kyiv", "Ukraine"): [50.450001, 30.523333],
               ("Sundsvall", "Sweden"): [62.390811, 17.306927],
               ("Stockholm", "Sweden"): [59.334591, 18.063240],
               ("Malmo", "Sweden"): [55.604981, 13.003822]}



for city, country in cities_coords:
    text = f"""
            <h4 style="color:green;">{city}</h4>
            <h5 style="color":"green">
                <table style="text-align: right;">
                    <tr>
                        <th>Country:</th>
                        <td><b>{country}</b></td>
                    </tr>
                    """
    for column in recent_weather_data.columns:
        text += f"""
                    <tr>
                        <th>{column}:</th>
                        <td>{recent_weather_data.loc[city][column]}</td>
                    </tr>"""
    text += """</table>
                    </h5>"""

    # text = f'<h3 style="color:green;">{city}</h3><h4>Air quality: 12;<br>Temperature: 24</h4>'
    folium.Marker(
        cities_coords[(city, country)], popup=text, tooltip=f"<strong>{city}</strong>"
    ).add_to(my_map)


# call to render Folium map in Streamlit
folium_static(my_map)




st.button("Re-run")
