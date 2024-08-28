#!/bin/bash

# set -e  # Exit immediately if a command exits with a non-zero status.

# check if castle.venv exists
if [ -d "castle.venv" ]; then
    echo "castle.venv already exists. Let's deactivate it before running this script."
    deactivate
fi

rm -rf mininet castle.venv __pycache__

# Check if mininet is installed
if ! command -v mn  &> /dev/null; then
    echo 'mininet is not installed. Installing...'
    git clone git://github.com/mininet/mininet
    cd mininet
    ./util/install.sh -a
    cd ..
fi

# Check if we are at Mininet directory or Tests directory
if pwd | grep -q "Tests" ; then
    cd ..
fi

pwd

# # Create and activate virtual environment
python3 -m venv castle.venv
source castle.venv/bin/activate

# # Install packages
pip install -e ../../

# # Update the Python executable path in the configuration file
sed -i 's#^FILE_PATH=.*#FILE_PATH='"$(which python3)"'#' config.cfg

# Run the test
python3 main.py --env emu --max_step 3 --max_episode 1 --scenario Scenario2

deactivate

# Clean up
read -p "Do you want to remove Mininet, the virtual environment, and __pycache__? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf mininet castle.venv __pycache__
fi
