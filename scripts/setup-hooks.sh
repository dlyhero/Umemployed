#!/bin/bash

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pip install pre-commit
pre-commit install

echo "Pre-commit hooks installed successfully!"
echo "Run 'pre-commit run --all-files' to check all files now."
