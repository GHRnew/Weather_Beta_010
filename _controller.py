# locations.json --->   _controller.py   ---> Runs the scripts
# This script is triggered by the Synology Task Scheduller, at the moment "Task 17 _controller Weather_Beta 010"
# Shall be combined with the locations.json and the task schedule for _controller.py within the Synology Task Scheduler
# 
# Functiion "should_run_script_for_location"
# This _conntroller will start all scripts (see ** below) listed in the structure scripts = [ ... ], one after the other.
# This _conntroller will start all scripts for the LOCATIONS listed in the locations.json, according to the parameter "running_period"
#   If "running_period": "each_start", this script will start scripts = [ ... ] at each start of this script.
#   If "running_period": "full_hour_only", this script will start the scripts = [ ... ] 
#       only if the time_now is within the first 30 seconds past full hour.
#
# ** Function "should_run_script_at_all"
# All scripts will be started, except those explicitelly listed in the function "should_run_script_at_all".


import json
import os
import sys
import subprocess
import platform  
import logging
from datetime import datetime

def setup_logging():
    script_path = os.path.dirname(os.path.abspath(__file__))
    log_filename = 'logging.txt'
    log_files_directoryName = 'log_files'
    log_files_path = os.path.join(script_path, log_files_directoryName)
    absolute_log_filename = os.path.join(log_files_path, log_filename)
    if not os.path.exists(log_files_path):
        os.makedirs(log_files_path)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(absolute_log_filename)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s _controller %(levelname)s: %(message)s'))

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    return logger


def run_script_unix(script_name, location, logger):
    try:
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        venv_path = '/volume1/GHR_weather_env'
        command = f'source {venv_path}/bin/activate && python3 {script_path} {location}'
        subprocess.run(command, shell=True, check=True)
        logger.info(f"Successfully ran {script_name} for {location} on Unix")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_name} for {location} on Unix: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        # sys.exit(1)


def run_script_windows(script_name, location, logger):
    try:
        script_path = os.path.join(os.path.dirname(__file__), script_name)
        venv_path = 'C:\\Users\\Goran\\OneDrive\\Programing\\Python\\pythonvenv\\GPT4'
        command = f'{venv_path}\\Scripts\\activate && python {script_path} {location}'
        subprocess.run(command, shell=True, executable='C:\\Windows\\System32\\cmd.exe', check=True)
        logger.info(f"Successfully ran {script_name} for {location} on Windows")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error running {script_name} for {location} on Windows: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        # sys.exit(1)


def should_run_script_for_location(running_period, time_now):
    if running_period == "each_start":
        return True
    elif running_period == "full_hour_only":
        return time_now.minute == 0 and time_now.second <= 30
    elif running_period == "no_run":
        return False
    return False


# Default: Check if the script_name may run
# The script 005_B_Log_API_response.py may run only if within 30 sec past the full hour.
# Must be combined with the locations.json and trigger times within Synology Task Scheduler
def should_run_script_at_all(script_name, time_now):
    if script_name == "005_B_Log_API_response.py":
        return time_now.minute == 00 and time_now.second <= 30
    return True  # This will allow other scripts to run irrespective of the time condition


def load_locations(logger):
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'locations.json')
        with open(config_path, 'r') as file:
            config = json.load(file)
        return config
    except Exception as e:
        logger.error(f"Error loading locations: {e}")
        logger.error("xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        sys.exit(1)


def main():
    logger = setup_logging()
    logger.info("Starting _controller script")

    locations_config = load_locations(logger)

    scripts = [
        "000_B_Perform_one_call.py",
        "005_B_Log_API_response.py",
        "010_B_Decode_current_weather.py",
        "020_B_Decode_minutely_forecast.py",
        "025_B_Plot_precipitation.py",
        "030_B_Decode_hourly_forecast.py",
        "035_B_Plot_temperature.py",
        "036_B_Plot_HCP.py"
        # Add the names of the other four scripts here
    ]

    # Capture the start time at the beginning of the script execution
    time_now = datetime.now()

    # Determine the operating system
    os_system = platform.system()
    run_script = run_script_windows if os_system == "Windows" else run_script_unix


    for location, config in locations_config.items():
        if should_run_script_for_location(config.get("running_period", ""), time_now):
            for script in scripts:
                if should_run_script_at_all(script, time_now):
                    run_script(script, location, logger)
                else:
                    logger.info(f"Skipping {script} as 'should_run_script_at_all returns 'no'.")
        else:
            logger.info(f"Skipping {location} as 'should_run_script_for_location' returns 'no'.")

    logger.info("Finished processing all scripts =====================================================================================")


if __name__ == "__main__":
    main()



