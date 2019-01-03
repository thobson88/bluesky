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
    printf "Please install python-pip\n"
    exit 1
fi

if [ $# -eq 1 ]; then
    venvname=$1
else
    venvname="venv"
fi

if [ -e $venvname ]; then
    printf "Virtual environment %s already exists.\nPlease remove or specify a different name as arg1.\n" $venvname
    exit 1
fi

# Check for virtualenv
if command -v virtualenv &>/dev/null; then
    printf "Found virtualenv\n"
else
    printf "Please install virtualenv\n"
    exit 1
fi

# Create a virtual environment.
printf "Creating virtual environment: $venvname\n"
pip install --upgrade virtualenv
virtualenv -p python3 $venvname

printf "Activating virtual environment\n"
source $venvname/bin/activate

printf "Installing dependencies\n"
pip install -r requirements.txt

status=$?
if [[ $status != 0 ]]; then
    printf "Failed to install dependencies.\n"
    exit 1
fi

# If running on a mac, apply this matplotlib fix:
# https://markhneedham.com/blog/2018/05/04/python-runtime-error-osx-matplotlib-$
if [[ $(uname -s) == Darwin ]]; then
    file=$HOME/.matplotlib/matplotlibrc
    if [ ! -e $file ]; then
        printf "Adding ~/.matplotlib/matplotlibrc\n"
        echo "backend: TkAgg" >> $HOME/.matplotlib/matplotlibrc
    fi
fi

# matplotlib imports tkinter
python -c "import tkinter"
status=$?
if [[ $status != 0 ]]; then
    printf "Please install python3-tk\n"
    exit 1
fi

printf "Installation successful\n"
printf "To run BlueSky in headless mode:\n"
printf "> source $venvname/bin/activate\n"
printf "> python BlueSky.py --headless\n"
