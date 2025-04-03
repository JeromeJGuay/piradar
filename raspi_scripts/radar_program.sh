#! /bin/bash

# Make sur the eth0 is up. It could have been turn down to use the wifi.
ifup eth0

# Run the actual program
/home/capteur/program/piradar/.venv/bin/python3 /home/capteur/program/piradar/piradar/scripts/run_always_on.py
