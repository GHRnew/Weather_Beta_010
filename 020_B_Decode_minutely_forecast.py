# <WeinheimerStr_55>.json   --->   020_B_Decode_minutely_forecast.py   --->   <WeinheimerStr_55>_minutely_forecast.txt

import json
import os
import logging
import sys
from datetime import datetime
from zoneinfo import ZoneInfo # A nice time zones overview https://www.timeanddate.com/time/map/

LOCATION_NAME = sys.argv[1]  # The first argument is the script name, so we use the second one.
# Load the location name from command-line arguments
# LOCATION_NAME = "WeinheimerStr_55"
# LOCATION_NAME ="EttlingerStr_8"


def format_unix_time(unix_time, time_zone):
    tz = ZoneInfo(time_zone)
    return datetime.fromtimestamp(unix_time, tz).strftime('%d.%m.%Y %H:%M')


def append_units(key, value, unit_type):
    units_metric = {
        'temp': '°C', 'feels_like': '°C', 'dew_point': '°C',
        'humidity': '%', 'clouds': '%', 'pop': '%'
    }
    units_imperial = {
        'temp': '°F', 'feels_like': '°F', 'dew_point': '°F',
        'humidity': '%', 'clouds': '%', 'pop': '%'
    }
    units = units_metric if unit_type == "metric" else units_imperial
    return f"{value}{units.get(key, '')}"


def read_and_format_minutely_weather(json_file_path, time_zone, logger):
    try:
        logger.info(f"Reading minutely weather data from {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        minutely_data = data.get('minutely', [])
        if not minutely_data:
            logger.error(f"No minutely weather data found in {json_file_path}")
            logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            sys.exit(1)

        # Header line
        formatted_lines = ["Date and Time,Precipitation (mm)"]

        for minute in minutely_data:
            time = format_unix_time(minute['dt'], time_zone)
            precipitation = minute['precipitation']
            line = f"{time},{precipitation}"
            formatted_lines.append(line)

        logger.info("Successfully processed and formatted minutely weather data.")
        return "\n".join(formatted_lines)
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {json_file_path}: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except FileNotFoundError:
        logger.error(f"Weather data file not found: {json_file_path}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error occurred while processing minutely weather data: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    return None


def write_minutely_forecast_to_file(output_file_path, formatted_data, logger):
    if not formatted_data:
        logger.error("No data provided to write to file.")
        return
    try:
        with open(output_file_path, 'w', encoding='utf-8') as file:
            file.write(formatted_data)
        logger.info(f"Minutely weather data successfully written to {output_file_path}")
    except FileNotFoundError:
        logger.error(f"Output file not found: {output_file_path}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except IOError as e:
        logger.error(f"IO error occurred while writing to file {output_file_path}: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    except Exception as e:
        logger.exception(f"Unexpected error occurred while writing to file {output_file_path}: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)


def extract_parameter_value(location_config, parameter_name, logger, location_name_for_logging_only):
    try:
        value = location_config[parameter_name]  # Retrieve the parameter from the location config
    except KeyError:
        logger.error(f"'{parameter_name}' key not found in the configuration for {location_name_for_logging_only}.")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    return value


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
        
        # If location, such as "WeinheimerStr_51"does not exist in the configuration file, log and exit.
        if not location_config:
            logger.error(f'Configuration data for the location "{LOCATION_NAME}" not found in the file "{location_configuration_data_file}".')
            logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            sys.exit(1)
        
        # If location exists in the configuration file process it
        else:
            json_file_name = f"{LOCATION_NAME}.json"
            output_file_name = f"{LOCATION_NAME}_minutely_forecast.txt"
            json_file_path = os.path.join(script_path, weather_data_path, json_file_name)
            output_file_path = os.path.join(script_path, weather_data_path, output_file_name)
            
            # Read the parameter values
            # LOCATION_NAME is given for a logging purposes only.
            time_zone = extract_parameter_value(location_config, 'time_zone', logger, LOCATION_NAME)
            
            # Read WeinheimerStr_55.json and format it into a long string 
            formatted_data = read_and_format_minutely_weather(json_file_path, time_zone, logger)
            
            # Write this long string into WeinheimerStr_55_minutely_forecast.txt
            write_minutely_forecast_to_file(output_file_path, formatted_data, logger)

            logger.info("OK, FINISHED NORMALLY -------------------------------------------------------------------------------")

    except Exception as e:
        # Catch any exception that was not already caught and logged
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
        return

if __name__ == "__main__":
    main()

