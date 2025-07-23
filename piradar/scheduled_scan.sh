#!/bin/bash

#HOME="/home/capteur/"

HOME=$(eval echo ~"$SUDO_USER")

PTYHON_INTERPRETER="$HOME/program/piradar/.venv/bin/python3"
PTYHON_SCRIPT="$HOME/program/piradar/piradar/scheduled_scan.py"
CONFIGS_DIR="$HOME/.piradar/"
 # ["DEBUG", "INFO", "WARNING", "ERROR"]
LOG_LEVEL="WARNING"
 # -W, --write-logging or leave empty for false.
WRITE_LOGGING="-W"

$PTYHON_INTERPRETER $PTYHON_SCRIPT $CONFIGS_DIR -L $LOG_LEVEL $WRITE_LOGGING
