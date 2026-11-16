#!/bin/bash
# Hourly signup outreach job, started by launchd (launchd/com.codepraxis.outreach.signups.plist).
# 1) sync new signups from the database, 2) claude -p sends due emails and handles replies (RUNBOOK.md).
# Shares the SF outreach lock so only one Gmail job runs at a time.
set -u
cd "$(dirname "$0")"
export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin

LOCK=/tmp/codepraxis-outreach.lock
if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +45)" ]; then rmdir "$LOCK"; fi  # stale
if ! mkdir "$LOCK" 2>/dev/null; then echo "$(date '+%F %T') signups skipped: another job running" >> runs.log; exit 0; fi
trap 'rmdir "$LOCK"' EXIT

echo "=== $(date '+%F %T %Z') signups" >> runs.log
../../backend/.venv/bin/python sync_db.py >> runs.log 2>&1 || ./notify.sh "Signup sync failed" "see outreach/signups/runs.log"

# Nothing to send and nobody to watch for replies: skip the claude run.
if [ "$(python3 signups.py due)" = "[]" ] && [ "$(python3 signups.py active)" = "[]" ]; then
  echo "=== $(date '+%F %T %Z') signups done (nothing due)" >> runs.log; exit 0
fi

TOOLS="Read Write Edit ToolSearch Bash(python3:*) Bash(./notify.sh:*) Bash(date:*) \
mcp__claude_ai_Gmail__send_message mcp__claude_ai_Gmail__search_threads mcp__claude_ai_Gmail__get_thread \
mcp__claude_ai_Gmail__reply mcp__claude_ai_HubSpot__search_crm_objects mcp__claude_ai_HubSpot__manage_crm_objects"

# Hooks off: Ninad's Stop hook would push "Claude finished" for every run. notify.sh sends the alerts that matter.
claude -p 'Signup outreach run. Read RUNBOOK.md in this folder and do sections 1, 2 and 3 exactly.' \
  --model claude-sonnet-5-5 --permission-mode dontAsk --allowedTools $TOOLS --name "outreach-signups" \
  --settings '{"disableAllHooks": true}' >> runs.log 2>&1
echo "=== $(date '+%F %T %Z') signups done (exit $?)" >> runs.log
