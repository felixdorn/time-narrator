#!/bin/bash

# This script automates the process of building and uploading the time-narrator package to PyPI.
#
# Usage:
#   ./release.sh
#
# Prerequisites:
#   - Python 3 and pip installed.
#   - A PyPI account with credentials configured for twine (or you will be prompted).

set -e # Exit immediately if a command exits with a non-zero status.

# --- STEP 1: Install/Update Build Dependencies ---
echo "INFO: Ensuring 'build' and 'twine' are installed..."
pip install --upgrade build twine

# --- STEP 2: Clean Previous Builds ---
echo "INFO: Removing old build artifacts..."
rm -rf dist/
rm -rf build/
rm -rf src/*.egg-info
rm -rf *.egg-info

# --- STEP 3: Build the Package ---
echo "INFO: Building the source distribution and wheel..."
uv run -m build

# --- STEP 4: Upload to PyPI ---
echo "INFO: Uploading the package to PyPI..."
echo "You will be prompted for your PyPI username and password."
uv run twine upload dist/*

echo ""
echo "✅ Successfully built and uploaded to PyPI!"
echo "You can view the new release at: https://pypi.org/project/time-narrator/"
