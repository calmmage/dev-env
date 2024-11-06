#!/bin/bash

if [ "$#" -ne 2 ]; then
    echo "Usage: $0 SECRET_NAME SECRET_VALUE"
    exit 1
fi

SECRET_NAME=$1
SECRET_VALUE=$2

python3 manage_secrets.py "$SECRET_NAME" "$SECRET_VALUE" 