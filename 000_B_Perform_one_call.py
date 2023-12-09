# locations <WeinheimerStr_55> --> 000_B_Perform_one_call.py (API) -->  <WeinheimerStr_55>.json

import json
import os
import sys
import requests
import logging

API30_KEY = os.environ["OPENWEATHERMAP_ONE_CALL_API30_KEY"]

LOCATION_NAME = sys.argv[1]  # The first argument is the script name, so we use the second one.
# Load the location name from command-line arguments
# LOCATION_NAME = "WeinheimerStr_55"
# LOCATION_NAME ="EttlingerStr_8"


def load_locations_data(locations_data_fileanme, location_name, logger):
    config_path = os.path.join(os.path.dirname(__file__), locations_data_fileanme)
    with open(config_path, 'r') as file:
        config = json.load(file)
    location_config = config.get(location_name)
    if not location_config:
        logger.error(f'Configuration data for the location "{LOCATION_NAME}" not found in the file "{locations_data_fileanme}".')
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    return location_config


def extract_parameter_value(location_config, parameter_name, logger, location_name_for_logging_only):
    try:
        value = location_config[parameter_name]  # Retrieve the parameter from the location config
    except KeyError:
        logger.error(f"'{parameter_name}' key not found in the configuration for {location_name_for_logging_only}.")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    return value


def CallAPI_saveJSON(location_config, json_filename, logger, location_name_for_logging_only):
    # Read the parameter values 
    lat = extract_parameter_value(location_config, 'lat', logger, location_name_for_logging_only)
    lon = extract_parameter_value(location_config, 'lon', logger, location_name_for_logging_only)
    units = extract_parameter_value(location_config, 'units', logger, location_name_for_logging_only)
    lang = extract_parameter_value(location_config, 'lang', logger, location_name_for_logging_only)
    
    # Perform API call
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units={units}&lang={lang}&appid={API30_KEY}"
    try:
        logger.info(f"Fetching weather data from Internet")
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # This will raise an HTTPError if the HTTP request returned an unsuccessful status code
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error occurred: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error occurred: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from OpenWeatherMap API: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)

    # Save the response content to a file
    try:
        with open(json_filename, 'w') as file:
            json.dump(response.json(), file, indent=4)
            logger.info(f"Weather data saved successfully to {json_filename}")
    except IOError as e:
        logger.error(f"Error writing data to file: {json_filename}: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
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
    logger.setLevel(logging.FATAL)  # Set the logger's level
    # Create a handler for writing to a file
    file_handler = logging.FileHandler(absolute_log_filename)
    file_handler.setLevel(logging.FATAL)  # Set the file handler's level
    file_handler.setFormatter(logging.Formatter(f'%(asctime)s {script_name} %(levelname)s: %(message)s'))
    
    # Create a handler for writing to the console
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.FATAL)  # Set the stream handler's level
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

        # Construct the file name for storage of weather data, for example WeinheimerStr_55.json
        json_file_name = f"{LOCATION_NAME}.json"
        json_file_path = os.path.join(script_path, weather_data_path, json_file_name)

        # Fetch the data from the API and store it to the "WeinheimerStr_55.json"
        # LOCATION_NAME is given for a logging purposes only.
        CallAPI_saveJSON(location_config, json_file_path, logger, LOCATION_NAME)
    
        logger.info("OK, FINISHED NORMALLY -------------------------------------------------------------------------------")
    
    except Exception as e:
        # Catch any exception that was not already caught and logged
        logger.error(f"An unexpected error occurred in Section 010 Perform One Call: {e}")
        sys.exit(1)
        return
    
if __name__ == "__main__":
    main()