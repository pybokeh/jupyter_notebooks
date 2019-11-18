#!/usr/bin/env bash
set -e
apt-get update
apt-get -y install build-essential
echo "Getting Python packages..."
pip install -U --no-cache-dir -r requirements.txt
rm requirements.txt
echo "Done!"
