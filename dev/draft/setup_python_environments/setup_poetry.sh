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

get_git_root_of_script() {
    # Get the directory path where the script is located
    local script_dir
    script_dir=$(dirname "$1")

    # Change to the directory where the script is located
    cd "$script_dir" || return 1

    # Get the Git root directory of the directory where the script is located
    local git_root
    git_root=$(git rev-parse --show-toplevel 2> /dev/null)

    # Change back to the original directory
    cd - > /dev/null

    # If git_root is empty, it means the directory is not in a Git repository
    if [ -z "$git_root" ]; then
        echo "Not a Git repository"
        return 1
    fi

    # Return the Git root directory path
    echo "$git_root"
}

# Example usage
# git_root=$(get_git_root_of_script "$0")
# echo "Git root directory: $git_root"
# endregion Utils

# This is a script to setup poetry environment for calmmage

# idea 0: take the requirements list from the calmmage dev env repo

# idea 1: determine the root path
# by default - ~/.calmmage
# if the user has set the CALMMAGE_ROOT_PATH environment variable, use that

# idea 2: if any of the envs already exist - update them to the latest requirements files

# Determine the root path
root_path="${CALMMAGE_ROOT_PATH:-$HOME/.calmmage}"
dir_path=$(dirname "$0")
repo_root_path=$(get_git_root_of_script "$0")

# Step 1: Make sure poetry is installed
if ! command -v poetry &> /dev/null; then
    log INFO "Poetry not found. Installing..."
    brew install poetry
else
    log INFO "Poetry is already installed."
fi

# Display poetry version
poetry --version

setup_poetry() {
    # Step 2: Determine the path of the poetry config file
    poetry_config_path="$repo_root_path/pyproject.toml"
    log INFO "Poetry config path: $poetry_config_path"

    # Step 3: Create and install the poetry environment to root_path
    log INFO "Creating and installing poetry environment..."
    poetry config virtualenvs.path "$root_path"
    poetry install --no-root

    # Step 4: Get the Python path for the created poetry environment
    python_path=$(poetry env info --path)/bin/python
    log INFO "Python path of the poetry environment: $python_path"

    # Step 5: Save the Python path to an environment variable
    export CALMMAGE_PYTHON_PATH="$python_path"
    log INFO "Python path saved to the environment variable CALMMAGE_PYTHON_PATH"
}
