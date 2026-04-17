#!/bin/bash
# STC Dispatcher - Supercharge and route
# Usage: ./run.sh "fix the website"
#        echo "place bets" | ./run.sh
cd "$(dirname "$0")"
python3 dispatcher.py "$@"
