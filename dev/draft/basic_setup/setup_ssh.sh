#!/bin/bash

# generate ssh key
ssh-keygen -t rsa -b 4096 -C "

# run ssh-agent
eval "$(ssh-agent -s)"

# add ssh key to ssh-agent
ssh-add ~/.ssh/id_rsa