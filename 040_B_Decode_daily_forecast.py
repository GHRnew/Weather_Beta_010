# 040_B_Decode_daily_forecast.py
import json
import os
import sys
import logging
from datetime import datetime

LOCATION_NAME = sys.argv[1]  # The first argument is the script name, so we use the second one.
# Load the location name from command-line arguments
# LOCATION_NAME = "WeinheimerStr_55"
# LOCATION_NAME ="EttlingerStr_8"


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as file:
        config = json.load(file)
    return config

def setup_logging(log_filepath):
    logging.basicConfig(filename=log_filepath, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def format_unix_date(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime('%d.%m.%Y')

def append_units(key, value):
    units = {
        'temp': '°C', 'feels_like': '°C', 'dew_point': '°C', 'day': '°C', 'night': '°C',
        'eve': '°C', 'morn': '°C', 'pressure': 'hPa', 'humidity': '%', 
        'visibility': 'm', 'wind_speed': 'm/sec', 'rain': 'mm'
    }
    return f"{value}{units.get(key, '')}"

def read_and_format_daily_weather(json_file_path):
    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
        
        daily_data = data.get('daily', [])
        formatted_data = "Daily Weather Forecast:\n"
        for day in daily_data:
            date = format_unix_date(day['dt'])
            formatted_data += f"\nDate: {date}\n"
            for key, value in day.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        formatted_value = append_units(sub_key, sub_value)
                        formatted_data += f"{sub_key.replace('_', ' ').title()}: {formatted_value}\n"
                elif key == 'weather':
                    weather = value[0]
                    formatted_data += f"Weather: {weather['main']}: {weather['description']}\n"
                elif key not in ['dt', 'sunrise', 'sunset', 'moonrise', 'moonset', 'moon_phase']:
                    formatted_value = append_units(key, value)
                    formatted_data += f"{key.replace('_', ' ').title()}: {formatted_value}\n"
        return formatted_data
    except Exception as e:
        logging.error(f"Error processing daily weather data: {e}")
        return None

def write_to_file(output_file_path, formatted_data):
    if formatted_data:
        try:
            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(formatted_data)
            logging.info(f"Formatted daily weather data written to {output_file_path}")
        except Exception as e:
            logging.error(f"Error writing to file: {e}")

def main():
    config = load_config()
    location_config, folders = config.get(LOCATION_NAME), config.get("folders")
    if not location_config:
        logging.error("Location configuration not found.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_filepath = os.path.join(script_dir, folders['log_files'], os.path.splitext(os.path.basename(__file__))[0] + '.log')
    setup_logging(log_filepath)

    json_file_name = f"{LOCATION_NAME}.json"
    output_file_name = f"{LOCATION_NAME}_daily_forecast.txt"
    json_file_path = os.path.join(script_dir, folders['weather_data'], json_file_name)
    output_file_path = os.path.join(script_dir, folders['weather_data'], output_file_name)

    formatted_data = read_and_format_daily_weather(json_file_path)
    write_to_file(output_file_path, formatted_data)

if __name__ == "__main__":
    main()
