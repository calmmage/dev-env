#!/bin/zsh

# assume env vars:
# export CALMMAGE_DEV_ENV_PATH=/Users/petrlavrov/.calmmage/dev_env
# export CALMMAGE_POETRY_ENV_PATH=$(poetry env info --path)
source ~/.zprofile
script_path ="$CALMMAGE_DEV_ENV_PATH/dev/draft/dev_env_rework/sample_script.py"
echo "script_path: $script_path"
# assume runp alias is defined
runp $script_path

# todo: try to run this in launchd
# todo: try to run this in raycast


