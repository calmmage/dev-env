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
    local repo_root_path="$1"
    local root_path="$2"
    local poetry_config_path="$repo_root_path/pyproject.toml"
    local symlink_path="$root_path/envs/poetry/calmmage-dev-env"

    log INFO "Poetry pyproject.toml path: $poetry_config_path"

    # Change to repo root directory
#     cd "$repo_root_path" || { log ERROR "Failed to change to repo root directory"; return 1; }
    pushd "$repo_root_path"

    log INFO "Updating dev_env repo..."
    if git pull --ff-only; then
        log INFO "Dev env repo updated successfully."
    else
        log WARN "Failed to update dev env repo. Continuing with existing version."
    fi

#     poetry config virtualenvs.path "$root_path/envs/poetry"
#     poetry config virtualenvs.in-project true

    log INFO "Running poetry install to ensure environment is up to date..."
    if poetry install; then
        log INFO "Poetry environment updated successfully."
    else
        log ERROR "Failed to update poetry environment."
        return 1
    fi

    local env_path=$(poetry env info --path)

    if [ -L "$symlink_path" ]; then
        if [ "$(readlink "$symlink_path")" = "$env_path" ]; then
            log INFO "Symlink is correct."
        else
            log INFO "Updating existing symlink..."
            ln -sfn "$env_path" "$symlink_path"
        fi
    else
        log INFO "Creating new symlink..."
        mkdir -p "$(dirname "$symlink_path")"
        ln -sf "$env_path" "$symlink_path"
    fi

    local python_path="$symlink_path/bin/python"
    log INFO "Python path of the poetry environment: $python_path"

#     export CALMMAGE_PYTHON_PATH="$python_path"
#     log INFO "Python path saved to the environment variable CALMMAGE_PYTHON_PATH"
    log INFO "Setup complete. New aliases available: 'run_py' and 'run'"
    log INFO "Use 'run_py' for Python scripts and 'run' for auto-detected executables"
    log INFO "Aliases will be setup by setup_dev_env script and available in your .zshrc or .alias files"
    popd >> null
}

setup_poetry "$repo_root_path" "$root_path"