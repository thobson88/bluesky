#!/bin/bash

# Check for python3.
if command -v python3 &>/dev/null; then
    printf "Found python3\n"
else
    printf "Please install python3\n"
    exit 1  
fi

# Check for pip.
if command -v pip &>/dev/null; then
    printf "Found pip\n"
else
    printf "Please install pip\n"
    exit 1
fi

if [ -e "venv" ]; then
    printf "Virtual environment venv already exists\n"
    exit 1
fi

# Create a virtual environment.
printf "Creating virtual environment: venv\n"
pip install --upgrade virtualenv
virtualenv -p python3 venv

printf "Activating virtual environment\n"
source venv/bin/activate

printf "Installing dependencies\n"
pip install -r requirements.txt

# If running on a mac, apply this matplotlib error fix:
# https://markhneedham.com/blog/2018/05/04/python-runtime-error-osx-matplotlib-$
if [[ $(uname -s) == Darwin ]]
then
    file=$HOME/.matplotlib/matplotlibrc
    if [ ! -e $file ]; then
        printf "Adding ~/.matplotlib/matplotlibrc\n"
        echo "backend: TkAgg" >> $HOME/.matplotlib/matplotlibrc
    fi
fi

printf "Installation successful\n"
printf "To run BlueSky in headless mode:\n"
printf "> source venv/bin/activate\n"
printf "> python3 BlueSky.py --headless\n"
