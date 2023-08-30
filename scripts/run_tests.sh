#!/bin/bash
set -e

pyright --stats

export PYTHONPATH=PyExpUtils
python3 -m unittest discover -p "*test_*.py"
