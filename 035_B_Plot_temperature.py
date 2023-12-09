# <WeinheimerStr_55>_hourly_forecast.txt   --->   035_B_Plot_temperature.py   --->   <WeinheimerStr_55>_hourly_temperature.jpeg

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import sys
import datetime
import json
import os
import logging

LOCATION_NAME = sys.argv[1]  # The first argument is the script name, so we use the second one.
# Load the location name from command-line arguments
# LOCATION_NAME = "WeinheimerStr_55"
# LOCATION_NAME ="EttlingerStr_8"


def parse_date_time(row):
    return datetime.datetime.strptime(f"{row['Date']} {row['Time']}", "%d.%m.%Y %H:%M")


def read_and_process_data(file_path, unit_type, logger):
    try:
        unit_symbol = '°C' if unit_type == 'metric' else '°F'
        wind_speed_unit = 'm/s'  # Assuming wind speed is in meters per second
        data = pd.read_csv(file_path, delimiter=',')
        data['Date_Time'] = data.apply(parse_date_time, axis=1)

        # Process temperature and other data as before
        data[f'Temperature {unit_symbol}'] = data['Temperature'].str.rstrip(unit_symbol).astype(float)
        data[f'Feels Like {unit_symbol}'] = data['Feels Like'].str.rstrip(unit_symbol).astype(float)
        data[f'Dew Point {unit_symbol}'] = data['Dew Point'].str.rstrip(unit_symbol).astype(float)

        # Process wind speed data
        data['Wind Speed (m/s)'] = data['Wind Speed'].str.rstrip(wind_speed_unit).astype(float)
        
        logger.info("Data read and converted")

        return data
    except Exception as e:
        logging.error(f"Error reading or processing file {file_path}: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)
        return None
    

def plot_data(data, location, jpeg_file_path, unit_type, logger):
    unit_symbol = '°C' if unit_type == 'metric' else '°F'
    fig, ax1 = plt.subplots(figsize=(12, 8))

    # Plot the temperature data
    color = 'tab:blue'
    ax1.set_xlabel('Date and Time')
    ax1.set_ylabel(f'Temperature ({unit_symbol})', color=color)
    ax1.plot(data['Date_Time'], data[f'Temperature {unit_symbol}'], label=f'Temperature ({unit_symbol})', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.axhline(0, color='black', linestyle='--', linewidth=1)
    for dt in data['Date_Time']:
        if dt.hour == 0 and dt.minute == 0:
            ax1.axvline(dt, color='black', linestyle='--', linewidth=1)

    # Instantiate a second y-axis for wind speed
    ax2 = ax1.twinx()  
    color = 'tab:gray'
    ax2.set_ylabel('Wind Speed (m/s)', color=color) 
    ax2.plot(data['Date_Time'], data['Wind Speed (m/s)'], label='Wind Speed (m/s)', color=color, linestyle='--', linewidth=1)
    ax2.tick_params(axis='y', labelcolor=color)

    # Title, grid and other settings
    ax1.set_title(f'48 Hours forecast for {location}. Temperature and Wind Speed.')
    ax1.grid(True)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y %H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))
    fig.autofmt_xdate()  # Rotate and align the x labels

    # Add legends for both y-axes
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='best', framealpha=0.5)

    fig.tight_layout()  # To fit everything into the figure without overlapping
    plt.savefig(jpeg_file_path, format='jpeg', bbox_inches='tight')
    logger.info(f"Combined Temperature and Wind Speed diagram saved in {jpeg_file_path}")




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
            # Read the parameter values
            # LOCATION_NAME is given for a logging purposes only.
            unit_type = extract_parameter_value(location_config, 'units', logger, LOCATION_NAME)
            
            weather_data_path = os.path.join(script_path, weather_data_directoryName)
            input_file_name = f"{LOCATION_NAME}_hourly_forecast.txt"
            jpeg_file_name = f"{LOCATION_NAME}_hourly_temperature.jpeg"
            
            hourly_file_path = os.path.join(weather_data_path, input_file_name)
            jpeg_file_path = os.path.join(weather_data_path, jpeg_file_name)

            data = read_and_process_data(hourly_file_path, unit_type, logger)
            plot_data(data, LOCATION_NAME, jpeg_file_path, unit_type, logger)
            # plt.show() # Do not show the diagram, for running via _controller script

            logger.info("OK, FINISHED NORMALLY -------------------------------------------------------------------------------")
    
    except Exception as e:
        # Catch any exception that was not already caught and logged
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
        return

if __name__ == "__main__":
    main()
