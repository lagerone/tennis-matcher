#!/bin/bash

SCRIPT=`readlink -f "$0"`
SCRIPT_PATH=`dirname $SCRIPT`

echo "SCRIPT_PATH=$SCRIPT_PATH"

pushd $SCRIPT_PATH
source venv/bin/activate
python src/match_cli.py
deactivate
popd