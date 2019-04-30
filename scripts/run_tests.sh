#!/bin/bash
set -e

export PYTHONPATH=PyExpUtils
python3 -m unittest discover -p "*test_*.py"
