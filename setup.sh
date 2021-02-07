#!/bin/bash

python3 -m venv venv
source venv/bin/activate
pip install -r src/dev_requirements.txt -U
pip install -r src/requirements.txt -U
deactivate