#!/usr/bin/env sh
# Build and test the Travel Nurse First-Contract Guide locally.
# No network access needed.
set -e
cd "$(dirname "$0")"
python3 build.py --check
python3 -m unittest discover -s tests -v
