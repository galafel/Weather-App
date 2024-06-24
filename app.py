import requests
import json
import pprint
import pytz
import pycountry
import streamlit as st
import pydeck as pdk
import pandas as pd
from timezonefinder import TimezoneFinder
from geopy.geocoders import Nominatim
from datetime import datetime


global global_user_settings
API_key = '805051f3f3d9845c991d0925f8e0d3cc'

def country_name_to_iso2(country_name):
    try:
        country = pycountry.countries.lookup(country_name)
        return country.alpha_2
    except LookupError:
        return None


def display_weather(temp_units="Celcius", location=["London", "GB"], i=0):
    # city = input("Please provide a city name: ")
    # country = input("Please provide an ISO 3166 country code: ")
    # city = 'Caracas'
    print(f"**** Entering display weather with index {i}")
    city = location[0]
    country = location[1]
    weather_data = {}
    r = requests.get(f'https://api.openweathermap.org/geo/1.0/direct?q={city},{country}&limit=5&appid={API_key}')
    result = r.json()
    # pprint.pp(result)
    lat = result[0]['lat']
    lon = result[0]['lon']
    # print(lat, lon)

    r2 = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_key}')
    result2 = r2.json()
    # pprint.pp(result2)

    print(f"     Current weather condition in {city},{country}: {result2['weather'][0]['description']}")
    weather_data['current_weather'] = f"{result2['weather'][0]['description']}"
    if temp_units == "Celcius":
        print(f"     Temperature: {(result2['main']['temp'] - 273.15):.2f}°C")
        weather_data['temp'] = f"{(result2['main']['temp'] - 273.15):.2f}°C"
    elif temp_units == "Kelvin":
        print(f"     Temperature: {(result2['main']['temp']):.2f}°K")
        weather_data['temp'] = f"{(result2['main']['temp']):.2f}°K"
    elif temp_units == "Fahrenheit":
        print(f"     Temperature: {(result2['main']['temp'] - 273.15) * 1.8 + 32:.2f}°F")
        weather_data['temp'] = f"{(result2['main']['temp'] - 273.15) * 1.8 + 32:.2f}°F"
    else:
        print("     Temperature unit settings invalid")
    
    print(f"     Humidity: {result2['main']['humidity']}%")
    weather_data['humidity'] = f"{result2['main']['humidity']}%"

    obj = TimezoneFinder()
    timezone = obj.timezone_at(lng=lon, lat=lat)
    # print(timezone)


    dt = pytz.utc.localize(datetime.utcnow())
    print(dt)
    formatted_user_time = dt.strftime("%A, %B %d, %Y, %I:%M %p")
    print(f"     Current date and time in UTC: {formatted_user_time}")
    time_in_city = dt.astimezone(pytz.timezone(timezone))
    print(time_in_city)
    formatted_location_time = time_in_city.strftime("%A, %B %d, %Y, %I:%M %p")
    print(f"     Current date and time in {city},{country}: {formatted_location_time}")
    print()

    
    return weather_data, lat, lon, formatted_user_time, formatted_location_time


def read_default_settings():
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data


def write_default_settings(json_object):
    with open('settings.json', 'w', encoding='utf-8') as f:
        data = {}
        data['temp_units'] = json_object["temp_units"]
        data['def_location'] = json_object["def_location"]
        data['fav_locations'] = json_object["fav_locations"]
        json.dump(data, f, ensure_ascii=False, indent=4)


def main():
    settings = read_default_settings()

    st.title("Weather App")

    if 'input_country' not in st.session_state:
        st.session_state.input_country = ''
    if 'input_city' not in st.session_state:
        st.session_state.input_city = ''
    if 'last_input' not in st.session_state:
        st.session_state.last_input = None
    if 'last_fav' not in st.session_state:
        st.session_state.last_fav = None

    input_country = st.text_input("Enter Country", st.session_state.input_country)
    input_city = st.text_input("Enter City", st.session_state.input_city)
    selected_country = st.selectbox("Select Country from Favorites", [city_country_pair[1] for city_country_pair in settings["fav_locations"]])
    selected_city = st.selectbox("Select City from Favorites", [city_country_pair[0] for city_country_pair in settings["fav_locations"]])

    if st.button("Clear Input"):
        st.session_state.input_country = ''
        st.session_state.input_city = ''
        st.experimental_rerun()

    st.session_state.input_country = input_country
    st.session_state.input_city = input_city

    input_country_iso = country_name_to_iso2(input_country)
    input_location = [input_city, input_country_iso]

    if input_city and input_country:
        if st.session_state.last_input != input_location:
            weather_data, lat, lon, formatted_user_time, formatted_location_time = display_weather(settings['temp_units'], input_location)
            st.session_state.last_input = input_location
            st.session_state.last_fav = None
    else:
        country_iso = country_name_to_iso2(selected_country)
        fav_location = [selected_city, country_iso]
        if st.session_state.last_fav != fav_location:
            weather_data, lat, lon, formatted_user_time, formatted_location_time = display_weather(settings['temp_units'], fav_location)
            st.session_state.last_fav = fav_location
            st.session_state.last_input = None

    if 'weather_data' in locals():
        st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
        st.metric("Temperature: ", weather_data['temp'])
        st.metric("Humidity: ", weather_data['humidity'])
        st.metric("Weather Conditions: ", weather_data['current_weather'])
        st.write(f"UTC Time: {formatted_user_time}")
        st.write(f"Local Time: {formatted_location_time}")




if __name__ == "__main__":
    main()