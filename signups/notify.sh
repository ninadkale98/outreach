#!/bin/bash
# Push a phone notification to Ninad via Pushover. Keys: ~/.config/codepraxis/pushover.env
#   ./notify.sh "Title" "Message"
source "$HOME/.config/codepraxis/pushover.env"
curl -s --form-string "token=$PUSHOVER_TOKEN" --form-string "user=$PUSHOVER_USER" \
  --form-string "title=$1" --form-string "message=$2" https://api.pushover.net/1/messages.json >/dev/null
