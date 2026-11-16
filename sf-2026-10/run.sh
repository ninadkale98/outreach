#!/bin/bash
# One headless outreach job, started by launchd (see launchd/*.plist). Independent of VS Code.
#   ./run.sh send | replies | refill
# Output goes to runs.log. Only one job runs at a time.
set -u
cd "$(dirname "$0")"
export PATH=/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin
MODE="$1"

LOCK=/tmp/codepraxis-outreach.lock
if [ -d "$LOCK" ] && [ -n "$(find "$LOCK" -maxdepth 0 -mmin +45)" ]; then rmdir "$LOCK"; fi  # stale
if ! mkdir "$LOCK" 2>/dev/null; then echo "$(date '+%F %T') $MODE skipped: another job running" >> runs.log; exit 0; fi
trap 'rmdir "$LOCK"' EXIT

case "$MODE" in
  send)    PROMPT='SF outreach SEND BATCH. Read RUNBOOK.md in this folder and follow the "Send batch" section exactly.' ;;
  replies) PROMPT='SF outreach REPLY CHECK. Read RUNBOOK.md in this folder and follow the "Reply check" section exactly.' ;;
  refill)  PROMPT='SF outreach QUEUE REFILL. Read RUNBOOK.md in this folder and follow the "Refill" section exactly.' ;;
  *) echo "usage: run.sh send|replies|refill"; exit 1 ;;
esac

TOOLS="Read Write Edit ToolSearch Bash(python3:*) Bash(./notify.sh:*) Bash(date:*) \
mcp__claude_ai_Gmail__send_message mcp__claude_ai_Gmail__search_threads mcp__claude_ai_Gmail__get_thread \
mcp__claude_ai_Gmail__reply mcp__claude_ai_HubSpot__search_crm_objects mcp__claude_ai_HubSpot__manage_crm_objects \
mcp__claude_ai_Apollo_io__apollo_mixed_people_api_search mcp__claude_ai_Apollo_io__apollo_mixed_companies_search \
mcp__claude_ai_Apollo_io__apollo_people_bulk_match mcp__claude_ai_Apollo_io__apollo_usage_stats_credit_usage_stats"

echo "=== $(date '+%F %T %Z') $MODE" >> runs.log
# Hooks off: Ninad's Stop hook would push "Claude finished" for every run. notify.sh sends the alerts that matter.
claude -p "$PROMPT" --model claude-sonnet-5-5 --permission-mode dontAsk --allowedTools $TOOLS --name "outreach-$MODE" \
  --settings '{"disableAllHooks": true}' >> runs.log 2>&1
echo "=== $(date '+%F %T %Z') $MODE done (exit $?)" >> runs.log
