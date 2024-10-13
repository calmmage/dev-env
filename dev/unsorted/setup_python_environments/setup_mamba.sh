#!/bin/bash

# region Utils
# Logging function
log() {
    local log_level=$1
    shift
    local log_message="$@"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    local script_name=$(basename "$0")
    case $log_level in
        INFO)
            echo -e "$timestamp [$script_name] [INFO] $log_message"
            ;;
        WARNING)
            echo -e "$timestamp [$script_name] [WARNING] $log_message"
            ;;
        ERROR)
            echo -e "$timestamp [$script_name] [ERROR] $log_message" >&2
            ;;
        *)
            echo -e "$timestamp [$script_name] [UNKNOWN] $log_message"
            ;;
    esac
}

# Example usage
# log INFO "This is an info message."
# log WARNING "This is a warning message."
# log ERROR "This is an error message."
# endregion Utils

# This is a script to setup mamba environment for calmmage

# idea 0: take the requirements list from the calmmage dev env repo

# idea 1: determine the root path
# by default - ~/.calmmage
# if the user has set the CALMMAGE_ROOT_PATH environment variable, use that

# idea 2: if any of the envs already exist - update them to the latest requirements files

