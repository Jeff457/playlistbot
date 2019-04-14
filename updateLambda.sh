#!/usr/bin/env bash

# get the full path to the script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
ZIP=$DIR/playlist-bot.zip

# remove existing archive
rm $ZIP

# add dependencies to archive
cd playlist-bot/package
zip -r9 $ZIP .

# add lambda function and helpers to archive
cd ..
zip -g $ZIP playlistbot.py spotify.py youtube.py

# update lambda function
# aws lambda update-function-code --function-name playlist-bot --zip-file fileb://$ZIP