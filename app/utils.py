# Import dependencies
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from config import google_api_key
import json
import requests
import sqlite3
from sqlalchemy import create_engine

# Construct Google Geocoding API query
# https://developers.google.com/maps/documentation/geocoding/intro
base_url = "https://maps.googleapis.com/maps/api/geocode/json"
params = {"key": google_api_key}

# Retrieve API results from city, state information
def address2api(address):
    '''
    Retrieve API results based on city and state information
    INPUT:
        address (string): name of city and state, e.g. Evanston, IL
    OUTPUT:
        results (list) - list of API results of the particular address
    '''
    params['address'] = address
    print(f"Retrieving Results for {address}.")

    response = requests.get(base_url, params=params).json()
    results = response.get('results')

    return results


# Retrieve lat and long information from API results of a particular address
def api2latlng(results):
    '''
    Retrieve latitude and longitude information from API results
    INPUTS:
        results (list) - list of API results of the particular address
    OUTPUTS:
        lat (str or NaN) - latitude of the address
        lng (str or NaN) - longitude of the address
    '''
    lat = np.nan
    lng = np.nan
    
    try:
        location = results[0]["geometry"]["location"]
        lat = location.get('lat', '')
        lng = location.get('lng', '')

    except:
        print("No lat lng information.")
        
    return lat, lng

# Convert input string to numeric
def str2num(input_string):
    """
    Convert input string to numeric
    INPUT:
        input_string (str): input string
    OUTPUT:
        output (float): converted value
    """
    try:
        input_string = input_string.replace(",", "").strip("%")
        output = float(input_string)
    except:
        output = np.nan
    return output