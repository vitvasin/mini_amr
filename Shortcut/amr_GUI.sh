#!/bin/bash

# Navigate to your project directory
cd /home/smr/workspaces/mini_amr/amrROS2_UI || exit 1

# Activate the virtual environment
source env/bin/activate

cd /home/smr/workspaces/mini_amr/amrROS2_UI/ICEAMR

# Run the Python script
python3 main.py
