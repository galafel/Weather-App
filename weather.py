global_user_settings = """{
    "temp_units": "Celcius",
    "def_location": ["London", "GB"],
    "fav_locations": [
        ["London", "GB"],
        ["New York", "US"],
        ["Tel Aviv", "IL"]
    ]
  }"""

import requests
import pprint
from datetime import datetime
import pytz
# !pip install tzwhere
# from tzwhere import tzwhere
# !pip install timezonefinder
from timezonefinder import TimezoneFinder

import json

API_key = '805051f3f3d9845c991d0925f8e0d3cc'


def display_weather(temp_units, location, i):
    # city = input("Please provide a city name: ")
    # country = input("Please provide an ISO 3166 country code: ")
    # city = 'Caracas'
    print(f"**** Entering display weather with index {i}")
    city = location[0]
    country = location[1]

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
    if temp_units == "Celcius":
        print(f"     Temperature: {(result2['main']['temp'] - 273.15):.2f}°C")
    elif temp_units == "Kelvin":
        print(f"     Temperature: {(result2['main']['temp']):.2f}°K")
    elif temp_units == "Fahrenheit":
        print(f"     Temperature: {(result2['main']['temp'] - 273.15) * 1.8 + 32:.2f}°F")
    else:
        print("     Temperature unit settings invalid")
    print(f"     Humidity: {result2['main']['humidity']}%")

    obj = TimezoneFinder()
    timezone = obj.timezone_at(lng=lon, lat=lat)
    # print(timezone)

    dt = pytz.utc.localize(datetime.now())
    formatted_user_time = dt.strftime("%A, %B %d, %Y, %I:%M %p")
    print(f"     Current date and time in UTC: {formatted_user_time}")
    time_in_city = dt.astimezone(pytz.timezone(timezone))
    formatted_location_time = time_in_city.strftime("%A, %B %d, %Y, %I:%M %p")
    print(f"     Current date and time in {city},{country}: {formatted_location_time}")
    print()


def read_default_settings():
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        # print(f"Settings temperature Units: {data['temp_units']}, \
        #         Favourite Locations: {data['fav_locations']}")
        return data


def write_default_settings(json_object):
    with open('settings.json', 'w', encoding='utf-8') as f:
        data = {}
        data['temp_units'] = json_object["temp_units"]
        data['def_location'] = json_object["def_location"]
        data['fav_locations'] = json_object["fav_locations"]
        json.dump(data, f, ensure_ascii=False, indent=4)


def change_temperature_units(new_temperature_units):
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        data['temp_units'] = new_temperature_units
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def add_favourite_location(new_favourite_location):
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        data['fav_locations'].append(new_favourite_location)
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def del_favourite_location(del_favourite_location):
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        if del_favourite_location in data['fav_locations']:
            data['fav_locations'].remove(del_favourite_location)
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def set_default_favourite_location(set_default_favourite_location):
    with open('settings.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        if set_default_favourite_location not in data['fav_locations']:
            data['fav_locations'].append(set_default_favourite_location)
            data['def_location'] = set_default_favourite_location
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# write_default_settings()
# read_default_settings()
# change_temperature_units("Kelvin")
# add_favourite_location("Caracas")
# del_favourite_location("New York")
# set_default_favourite_location("Colombia")


def user_default_settings():
    global_user_settings
    json_object = json.loads(global_user_settings)
    write_default_settings(json_object)


if __name__ == "__main__":
    user_default_settings()
    settings = read_default_settings()
    # pprint.pp(settings)
    for i, location in enumerate(settings['fav_locations']):
        display_weather(settings['temp_units'], location, i)