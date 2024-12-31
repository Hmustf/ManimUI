#!/bin/bash

# Get the directory where the script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate the virtual environment
source "$DIR/manim-env-py310/bin/activate"

# Run the application with warnings suppressed
PYTHONWARNINGS=ignore python "$DIR/manim_ui.py" 