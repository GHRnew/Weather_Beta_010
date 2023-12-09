# <WeinheimerStr_55>_hourly_forecast.txt   --->   035_B_Plot_temperature.py   --->   <WeinheimerStr_55>_hourly_HPC.jpeg

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import datetime
import sys
import os
import logging
import json

LOCATION_NAME = sys.argv[1]  # The first argument is the script name, so we use the second one.
# Load the location name from command-line arguments
# LOCATION_NAME = "WeinheimerStr_55"
# LOCATION_NAME ="EttlingerStr_8"

def parse_date_time(row):
    return datetime.datetime.strptime(f"{row['Date']} {row['Time']}", "%d.%m.%Y %H:%M")

def read_and_process_data(file_path, logger):
    try:
        data = pd.read_csv(file_path, delimiter=',')
        data['Date_Time'] = data.apply(parse_date_time, axis=1)
        data['Humidity %'] = data['Humidity %'].str.replace('%', '').astype(float)
        data['Clouds %'] = data['Clouds %'].str.replace('%', '').astype(float)
        data['Pop %'] = data['Pop %'].str.replace('%', '').astype(float)
        logger.info("HPS Data read")
        return data
    except Exception as e:
        logging.error(f"Error reading or processing file {file_path}: {e}")
        return None

def plot_data(data, location, jpeg_file_path, logger):
    plt.figure(figsize=(12, 8))

    plt.plot(data['Date_Time'], data['Pop %'], label='Probability of Precipitation / oborine (%)', linestyle='-', color='blue', linewidth=1) 
    plt.plot(data['Date_Time'], data['Humidity %'], label='Humidity (%)', linestyle='-.', color='green', linewidth=1) 
    plt.plot(data['Date_Time'], data['Clouds %'], label='Clouds (%)', linestyle='-.', color='orange', linewidth=1)  
    
    for dt in data['Date_Time']:
        if dt.hour == 0 and dt.minute == 0:
            plt.axvline(dt, color='black', linestyle='--', linewidth=1)
    plt.xlabel('Date and Time')
    plt.ylabel('Percentage (%)')
    plt.title(f'48 Hours Forecast for {location}: Humidity, Clouds, Precipitation (Oborine).')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%Y %H:%M'))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.gca().xaxis.set_major_locator(mdates.HourLocator(interval=3))
    plt.legend(loc='best', framealpha=0.5)
    plt.tight_layout()
    logger.info("HPC diagram plotted")
    plt.savefig(jpeg_file_path, format='jpeg', bbox_inches='tight')
    logger.info(f"HPC diagram saved in {jpeg_file_path}")


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
            weather_data_path = os.path.join(script_path, weather_data_directoryName)
            input_file_name = f"{LOCATION_NAME}_hourly_forecast.txt"
            jpeg_file_name = f"{LOCATION_NAME}_hourly_HPC.jpeg"
            
            hourly_file_path = os.path.join(weather_data_path, input_file_name)
            jpeg_file_path = os.path.join(weather_data_path, jpeg_file_name)

            data = read_and_process_data(hourly_file_path, logger)
    
            plot_data(data, LOCATION_NAME, jpeg_file_path, logger)
            # plt.show() # Do not show the diagram, for running via _controller script

    
    except Exception as e:
        # Catch any exception that was not already caught and logged
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
        return



if __name__ == "__main__":
    main()
