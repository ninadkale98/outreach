#!/bin/bash
# Installs the outreach schedules as macOS LaunchAgents so they run without VS Code / Claude open.
#   ./install.sh            install + load
#   ./install.sh uninstall  stop + remove
set -e
cd "$(dirname "$0")/launchd"
U=$(id -u)
JOBS="com.codepraxis.awake com.codepraxis.outreach.send com.codepraxis.outreach.replies com.codepraxis.outreach.refill"
for j in $JOBS; do launchctl bootout gui/$U/$j 2>/dev/null || true; done
if [ "${1:-}" = uninstall ]; then
  for j in $JOBS; do rm -f ~/Library/LaunchAgents/$j.plist; done; echo "removed"; exit 0
fi
for j in $JOBS; do
  cp $j.plist ~/Library/LaunchAgents/
  launchctl bootstrap gui/$U ~/Library/LaunchAgents/$j.plist && echo "loaded $j"
done
launchctl list | grep codepraxis
