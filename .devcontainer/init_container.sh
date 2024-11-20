#!/bin/bash
echo "Running init_container.sh, use this script to install libraries etc."

set -e

pre-commit install

pip install -r .devcontainer/requirements.txt

pip install -e .
