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

# idea 1: determine the root path
# by default - ~/.calmmage
# if the user has set the CALMMAGE_ROOT_PATH environment variable, use that

# idea 2: if any of the envs already exist - update them to the latest requirements files

# idea 3: run setup_poetry, setup_mamba and setup_miniforge


# determine the root path of the repository and the dir in which this file is
dir_path=$(dirname "$0")
repo_root_path=$(get_git_root_of_script "$0")

log INFO "Repository root path: $repo_root_path"
log INFO "Directory path: $dir_path"

# determine paths of the scripts

poetry_script_path="$dir_path/setup_poetry.sh"
mamba_script_path="$dir_path/setup_mamba.sh"
miniforge_script_path="$dir_path/setup_miniforge.sh"

# run
log INFO "Running setup_poetry.sh"
bash "$poetry_script_path"

log INFO "Running setup_mamba.sh"
bash "$mamba_script_path"

log INFO "Running setup_miniforge.sh"
bash "$miniforge_script_path"