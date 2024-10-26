import requests
import time
import csv
import os
from datetime import datetime
from collections import defaultdict
from config.config import API_KEY, INTERVAL
from utils import pretty_print, get_timestamp

CITIES = ['Delhi', 'Mumbai', 'Chennai', 'Bangalore', 'Kolkata', 'Hyderabad']
API_URL = "http://api.openweathermap.org/data/2.5/weather?q={}&appid={}"

ALERT_THRESHOLDS = {
    'temp': 35,
    'weather_condition': 'Rain'
}

daily_data = defaultdict(list)


def get_weather_data(city, retries=3, timeout=5):
    url = API_URL.format(city, API_KEY)
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                data = response.json()
                if 'main' in data and 'weather' in data and data['weather']:
                    return data
                else:
                    print(f"Warning: Incomplete data for {city}")
                    return None
            else:
                print(f"Failed to retrieve data for {city} - Status Code: {response.status_code}")
                return None
        except requests.exceptions.Timeout:
            print(f"Timeout for {city}. Attempt {attempt + 1} of {retries}. Retrying...")
        except requests.exceptions.RequestException as e:
            print(f"Error for {city}: {e}")
            return None
    print(f"Failed to get data for {city} after {retries} attempts.")
    return None


def fetch_all_cities_weather():
    weather_data = {}
    for city in CITIES:
        data = get_weather_data(city)
        if data:
            weather_data[city] = process_weather_data(data)
    return weather_data


def process_weather_data(data):
    return {
        'city': data['name'],
        'temp': round(data['main']['temp'] - 273.15, 2),
        'weather_condition': data['weather'][0]['main'],
        'timestamp': get_timestamp()
    }


def store_daily_summary_to_csv(summary):
    filename = "daily_weather_summary.csv"
    file_exists = os.path.isfile(filename)

    # Update fieldnames to match keys in the summary dictionary
    fieldnames = ['city', 'temp', 'weather_condition', 'timestamp']

    with open(filename, mode='a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        writer.writerow(summary)


def run_weather_monitoring():
    while True:
        print(f"Fetching weather data at {get_timestamp()}")
        weather_data = fetch_all_cities_weather()
        for city, data in weather_data.items():
            pretty_print(data)
            store_daily_summary_to_csv(data)
        time.sleep(INTERVAL)


if __name__ == "__main__":
    run_weather_monitoring()
