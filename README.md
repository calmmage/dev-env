# Update 2024-10-14
- Нужен скрипт, который все разворачивает
    - Изначально этот скрипт на питоне - как его запустить?
    - Вариант 1 - пайчармом
    - Вариант 2 - poetry install, poetry run
    - dev_env/run.py
    
    ---
    
    - Что делает скрипт?
        1. Скачивает dev_env в ~/.calmmage/dev_env
            1. Обновляет
        2. Кладет все нужное в ~/.zshrc если его там нет
            1. путь до dev_env
            2. путь до poetry env
            3. source dev_env/resources/shell_profiles/.zshrc
            4. source dev_env/resources/shell_profiles/aliases
    1. Привязать скрипт к raycast setup_calmmage_dev_env
        1. Инструкция как настраивать raycast (может я ее уже писал? где-то…)
            1. extensions
            2. scripts
    2. Привязать к launchd чтобы daily гонялся-обновлялся
        1. Какой-то самодостаточный скрипт который может прогнаться даже если все сломано?







---
# New dev env

## [todo] install brew

## [done] setup ssh keys
[setup_ssh.sh](dev/unsorted/basic_setup/setup_ssh.sh)

## [done] setup github cli
[setup_gh.sh](dev/unsorted/basic_setup/setup_gh.sh)

## [wip] install python environments

## [todo] clone all projects

## idea: daily job to commit / push / pull all repos


# old dev env

## create project structure 

## setup zshrc and aliases

## raycast extensions

## launchd jobs


# one-off todos:

## add all utils to calmlib - to a beta section

## add all code snippets to calmapp / bot-lib - to a beta section

## add all code snippets to examples repo

## resolve 'migration' branches

## resolve leaked telegram token to a notion assistant repo

## resolve github tests failing - fix