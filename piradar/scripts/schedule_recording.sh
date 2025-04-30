#!/bin/bash

HOME=$(eval echo ~"$SUDO_USER")

PTYHON_INTERPRETER="$HOME/program/piradar/.venv/bin/python3"
PTYHON_SCRIPT="$HOME/program/piradar/piradar/scripts/basic_program.py"
CONFIG_FILES="$HOME/program/piradar/piradar/scripts/auto_configuration.ini"
 # -W, --write-logging or leave empty for false.
LOG_LEVEL="WARNING"
 # -W, --write-logging or leave empty for false.
WRITE_LOGGING="-W"

$PTYHON_INTERPRETER $PTYHON_SCRIPT $CONFIG_FILES $LOG_LEVEL $WRITE_LOGGING
