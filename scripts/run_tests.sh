#!/bin/bash
set -e

MYPYPATH=./typings mypy -p PyExpUtils

export PYTHONPATH=PyExpUtils
python3 -m unittest discover -p "*test_*.py"
