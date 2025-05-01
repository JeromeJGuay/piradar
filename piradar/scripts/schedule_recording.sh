#!/bin/bash

HOME="/home/capteur/"

PTYHON_INTERPRETER="$HOME/program/piradar/.venv/bin/python3"
PTYHON_SCRIPT="$HOME/program/piradar/piradar/scripts/programs/basic_program.py"
CONFIG_FILES="$HOME/program/piradar/piradar/scripts/configs/auto_configuration.ini"
 # ["DEBUG", "INFO", "WARNING", "ERROR"]
LOG_LEVEL="WARNING"
 # -W, --write-logging or leave empty for false.
WRITE_LOGGING="-W"

$PTYHON_INTERPRETER $PTYHON_SCRIPT $CONFIG_FILES -L $LOG_LEVEL $WRITE_LOGGING
