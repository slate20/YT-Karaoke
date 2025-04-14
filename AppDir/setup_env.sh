#!/bin/bash
cd "$(dirname "$0")"
python3 -m venv usr/lib/$APP_NAME/venv
usr/lib/$APP_NAME/venv/bin/pip install -r usr/share/$APP_NAME/requirements.txt
