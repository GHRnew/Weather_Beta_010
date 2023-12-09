# <WeinheimerStr_55>.json   --->   010_B_Decode_current_weather.py   --->   <WeinheimerStr_55>_current_weather.txt
#                                                                           <WeinheimerStr_55>_current_weather.jpeg

import json
import os
import logging
import sys
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime 
from zoneinfo import ZoneInfo # A nice time zones overview https://www.timeanddate.com/time/map/

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


def format_date_and_time(unix_time, time_zone):
    tz = ZoneInfo(time_zone)
    local_time = datetime.fromtimestamp(unix_time, tz)
    return local_time.strftime('%d.%m.%Y %H:%M')


def format_sun_times(sunrise_time, sunset_time, time_zone):
    tz = ZoneInfo(time_zone)
    sunrise_local_time = datetime.fromtimestamp(sunrise_time, tz).strftime('%H:%M')
    sunset_local_time = datetime.fromtimestamp(sunset_time, tz).strftime('%H:%M')
    return sunrise_local_time, sunset_local_time


def append_units(key, value, unit_type):
    units = {
        'temp': '°C' if unit_type == 'metric' else '°F',
        'feels_like': '°C' if unit_type == 'metric' else '°F',
        'dew_point': '°C' if unit_type == 'metric' else '°F',
        'humidity': '%',
        'clouds': '%',
        'pop': '%'
    }
    return f"{value}{units.get(key, '')}"


def read_and_format_current_weather(json_file_path, time_zone, unit_type, logger):
    try:        
        with open(json_file_path, 'r', encoding='utf-8') as file:
            logger.info(f"Reading weather data from {json_file_path}")
            data = json.load(file)

        current_data = data.get('current', {})
        if not current_data:
            logger.error(f"No current weather data found in {json_file_path}")
            logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            sys.exit(1)

        formatted_data = "Current Weather Data:\n"
        formatted_data += format_date_and_time(current_data.pop('dt'), time_zone) + '\n'

        # Extract and convert sunrise and sunset times
        sunrise_time = current_data.pop('sunrise')
        sunset_time = current_data.pop('sunset')
        sunrise_local_time, sunset_local_time = format_sun_times(sunrise_time, sunset_time, time_zone)

        # Add converted sunrise and sunset times to formatted data
        formatted_data += f"Sunrise: {sunrise_local_time}\n"
        formatted_data += f"Sunset: {sunset_local_time}\n"


        for key, value in current_data.items():
            if key == 'weather':
                weather_description = value[0]['description']
                value = f"{value[0]['main']}: {weather_description}"
            else:
                value = append_units(key, value, unit_type)  # Pass the unit_type here

            formatted_data += f"{key.replace('_', ' ').title()}: {value}\n"

        logger.info("Successfully processed and formatted current weather data.")
        return formatted_data    
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from file {json_file_path}: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)    
    except FileNotFoundError:
        logger.error(f"Weather data file not found: {json_file_path}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)    
    except Exception as e:
        logger.exception(f"Unexpected error occurred while processing weather data: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)    
    return None


def write_to_file(location_name, output_file_path, formatted_data, logger):
    if formatted_data:
        try:
            # Extracting date and time from formatted_data
            date_time_line = formatted_data.split('\n')[1]  # Assuming the date and time is always on the second line
            date_and_time = date_time_line.strip()  # Remove any leading/trailing whitespaces

            # Preparing new content with location and date and time
            new_content = f"Current Weather in: {location_name}\nDate and time: {date_and_time}\n" + "\n".join(formatted_data.split('\n')[2:])

            with open(output_file_path, 'w', encoding='utf-8') as file:
                file.write(new_content)
            logger.info(f"Formatted weather data written to {output_file_path}")
        
        except IOError as io_error:
            logger.error(f'IOError while writing to file {output_file_path}: {io_error}')
            logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            sys.exit(1)
        except OSError as os_error:
            logger.error(f'OSError while writing to file {output_file_path}: {os_error}')
            logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
            sys.exit(1)


def create_image_from_text_with_matplotlib(text_file_path, image_file_path, logger, fontsize=20):  # Default fontsize set to 20
    # Read the text from the file
    with open(text_file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Create a figure
    plt.figure(figsize=(12, 8))
    # Add text to the plot, now with the fontsize argument
    plt.text(0.05, 0.5, text, horizontalalignment='left', verticalalignment='center', wrap=True, fontsize=fontsize)
    
    # Remove axes
    plt.axis('off')

    # Save the figure as a JPEG
    plt.savefig(image_file_path, format='jpeg', bbox_inches='tight')
    logger.info(f"Text image saved in {image_file_path}")

    # Close the plot to free up memory
    plt.close()


def extract_parameter_value(location_config, parameter_name, logger, location_name_for_logging_only):
    try:
        value = location_config[parameter_name]  # Retrieve the parameter from the location config
    except KeyError:
        logger.error(f"'{parameter_name}' key not found in the configuration for {location_name_for_logging_only}.")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
    return value


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
            output_file_name = f"{LOCATION_NAME}_current_weather.txt"
            json_file_path = os.path.join(script_path, weather_data_path, json_file_name)
            output_file_path = os.path.join(script_path, weather_data_path, output_file_name)
            
            # Read the parameter values
            # LOCATION_NAME is given for a logging purposes only.
            unit_type = extract_parameter_value(location_config, 'units', logger, LOCATION_NAME)
            time_zone = extract_parameter_value(location_config, 'time_zone', logger, LOCATION_NAME)

            # Read json data, such as "WeinheimerStr_51,json" and convert to the output format
            formatted_data = read_and_format_current_weather(json_file_path, time_zone, unit_type, logger)
            # Save the formated data to a file 
            write_to_file(LOCATION_NAME, output_file_path, formatted_data, logger)

            image_file_path = f"{output_file_path.replace('.txt', '.jpeg')}"
            create_image_from_text_with_matplotlib(output_file_path, image_file_path, logger, fontsize=24)  # Specify desired font size here
            logger.info(f"Image file created: {image_file_path}")

            logger.info("OK, FINISHED NORMALLY -------------------------------------------------------------------------------")

    except Exception as e:
        # Catch any exception that was not already caught and logged
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
        return

if __name__ == "__main__":
    main()
