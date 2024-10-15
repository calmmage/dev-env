#!/bin/zsh

# source env vars from zprofile
# export CALMMAGE_DEV_ENV_PATH=/Users/petrlavrov/.calmmage/dev_env
# export CALMMAGE_POETRY_ENV_PATH=$(poetry env info --path)
source ~/.zprofile

script_path ="$CALMMAGE_DEV_ENV_PATHdev/draft/mvp/daily_job.py"
# echo "script_path: $script_path"
# assume runp alias is defined - source from zprofile
runp $script_path


