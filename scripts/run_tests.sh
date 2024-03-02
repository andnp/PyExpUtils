#!/bin/bash
set -e

source .venv/bin/activate

# pyright --stats

export PYTHONPATH=PyExpUtils
python3 -m unittest discover -p "*test_*.py"
