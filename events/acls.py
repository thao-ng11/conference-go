from lib2to3.pgen2.token import OP
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import json
import requests

def get_photo(city, state):
    # Create a dictionary for the headers to use in the request
    headers = {
    "Authorization" : PEXELS_API_KEY    
}   
    # Create the URL for the request with the city and state
    url = "https://api.pexels.com/v1/search"
    # Make the request
    params = {
    "query" : f'{city} {state}',
    "per_page" : 1,
}
    res = requests.get(url, params=params, headers=headers)
    # Parse the JSON response
    result = res.json()
    # Return a dictionary that contains a `picture_url` key and
    #   one of the URLs for one of the pictures in the response
    picture_dict = {
        "picture_url":result["photos"][0]['src']['original']
        }
    return picture_dict

def get_lat_lon(city, state):
    # Create the URL for the current weather API with the latitude
    #   and longitude
    geo_url = "http://api.openweathermap.org/geo/1.0/direct"
    geo_params = {"appid": OPEN_WEATHER_API_KEY, "q" : f"{city},{state},USA"}
    # Make the request
    res = requests.get(geo_url, params=geo_params)
    # Parse the JSON response
    the_json = res.json()
    # Get the latitude and longitude from the response
    lat = the_json[0]["lat"]
    lon = the_json[0]["lon"]
    return lat, lon

def get_weather_data(city, state):
    lat, lon = get_lat_lon(city, state)
    # Create the URL for the geocoding API with the city and state
    weather_url = "https://api.openweathermap.org/data/2.5/weather"
    weather_params = {
        "appid": OPEN_WEATHER_API_KEY,
        "lat" : lat,
        "lon" : lon,
        "units" : "imperials",
    }
    # Make the request
    res = requests.get(weather_url, params= weather_params)
    # Parse the JSON response
    the_json = res.json()
    # Get the main temperature and the weather's description and put
    #   them in a dictionary
    return {
            "temp" : the_json["main"]["temp"],
            "description" : the_json["weather"][0]["description"],
                }
    # Return the dictionary





