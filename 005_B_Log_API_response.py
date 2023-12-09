# <WeinheimerStr_55>.json   --->   005_B_Log_API_responses.py   --->   append to the <WeinheimerStr_55>_all_responses.csv
# Only if the parameter "store_all_responses": "yes" for the LOCATION_NAME

import json
import os
import sys
import csv
import logging
from datetime import datetime

LOCATION_NAME = sys.argv[1]  # The first argument is the script name, so we use the second one.
# Load the location name from command-line arguments
# LOCATION_NAME = "WeinheimerStr_55"
# LOCATION_NAME ="EttlingerStr_8"
# LOCATION_NAME = "MorrisCourt_4imp"

def load_locations_data(locations_data_filename, location_name, logger):
    config_path = os.path.join(os.path.dirname(__file__), locations_data_filename)
    with open(config_path, 'r') as file:
        config = json.load(file)
    location_config = config.get(location_name)
    logger.info(f"Location data loaded for {location_name}")
    if not location_config:
        logger.error(f'Configuration data for the location "{location_name}" not found in the file "{locations_data_filename}".')
        sys.exit(1)
    return location_config


def extract_parameter_value(location_config, parameter_name, logger, location_name_for_logging_only):
    try:
        value = location_config[parameter_name]  # Retrieve the parameter from the location config
        logger.info(f"Parameter extracted: {parameter_name}")
    except KeyError:
        logger.error(f"'{parameter_name}' key not found in the configuration for {location_name_for_logging_only}.")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    return value


def append_to_csv(file_path, data, header, logger):
    file_exists = os.path.isfile(file_path)
    try:
        with open(file_path, 'a', newline='') as file:
            writer = csv.writer(file)
            # Write header only if the file is being created for the first time
            if not file_exists or os.path.getsize(file_path) == 0:
                writer.writerow(header)
            writer.writerow(data)
        logger.info(f"csv file written into: {file_path}")
    except IOError as e:
        logger.error(f"Error writing data to file: {file_path}: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)


def format_csv_data(data, logger):
    try:
        # Define the header
        header = ['timezone', 'timezone_offset', 'dt', 'temperature', 'feels_like', 'pressure', 'humidity', 'uvi', 'clouds', 'wind_speed', 'wind_deg', 'wind_gust']
        
        # Extract the timezone and timezone_offset directly from the data
        timezone = data['timezone']
        timezone_offset = data['timezone_offset']

        # Now, define current_data using the 'current' key from the data
        current_data = data['current']
        dt = current_data['dt']  # This is the UNIX timestamp for the current data point
        temp = current_data['temp']
        feels_like = current_data['feels_like']
        pressure = current_data['pressure']
        humidity = current_data['humidity']
        uvi = current_data['uvi']
        clouds = current_data['clouds']
        wind_speed = current_data.get('wind_speed')
        wind_deg = current_data.get('wind_deg')
        wind_gust = current_data.get('wind_gust')
        
        # Prepare the data row
        csv_data = [timezone, timezone_offset, dt, temp, feels_like, pressure, humidity, uvi, clouds, wind_speed, wind_deg, wind_gust]
        logger.info(f"CSV data formatted")

        # Return both the header and the row data
        return header, csv_data
    except KeyError as e:
        logger.error(f"Key error occurred while formatting CSV data: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred while formatting CSV data: {e}")
        sys.exit(1)



def main():

    #region COMMON CODE START -------------------------------------------------------------------
    # Get the full path of the current script
    script_path = os.path.dirname(os.path.abspath(__file__))
    # Extract the script's name from the full path
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    # Use the common log file for all scripts
    log_filename = 'logging.txt'

    # Here are the coordinates, language, units etc for locations such as "WeinheimerStr_51"
    location_configuration_data_file = 'locations.json'

    # Directory for the weather data files
    weather_data_directoryName = 'weather_data'
    weather_data_path = os.path.join(script_path, weather_data_directoryName)

    # Directory for the log files
    log_files_directoryName  = 'log_files'
    log_files_path = os.path.join(script_path, log_files_directoryName)
    absolute_log_filename = os.path.join(log_files_path, log_filename)  # Include the file name in the path
    if not os.path.exists(log_files_path):
        os.makedirs(log_files_path)

    # Create a logger object
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Set the logger's level
    # Create a handler for writing to a file
    file_handler = logging.FileHandler(absolute_log_filename)
    file_handler.setLevel(logging.INFO)  # Set the file handler's level
    file_handler.setFormatter(logging.Formatter(f'%(asctime)s {script_name} %(levelname)s: %(message)s'))
    
    # Create a handler for writing to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)  # Set the stream handler's level
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    # Add both handlers to the logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    # Signal start
    logger.info("Program started")
    #endregion COMMON CODE END ------------------------------------------------------------------------

    try:
        # Read the locations data chect that the LOCATION exists
        location_config = load_locations_data(location_configuration_data_file, LOCATION_NAME, logger)
        
        # If location, such as "WeinheimerStr_51"does not exist in the configuration file, log and exit.
        if not location_config:
            logger.error(f'Configuration data for the location "{LOCATION_NAME}" not found in the file "{location_configuration_data_file}".')
            logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            sys.exit(1)

        # Read the parameter values
        # LOCATION_NAME is given for a logging purposes only.
        store_all_responses = extract_parameter_value(location_config, 'store_all_responses', logger, LOCATION_NAME)

        if store_all_responses == 'yes':
            json_file_name = f"{LOCATION_NAME}.json"
            json_file_path = os.path.join(script_path, weather_data_path, json_file_name)
            response_csv_file = os.path.join(script_path, weather_data_path, f"{LOCATION_NAME}_all_responses.csv")
            
            with open(json_file_path, 'r') as file:
                data = json.load(file)
            
            header, csv_data = format_csv_data(data, logger)
            append_to_csv(response_csv_file, csv_data, header, logger)




    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
