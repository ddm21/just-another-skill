#!/usr/bin/env bash
input=$(cat)

MODEL=$(echo "$input" | jq -r '.model.display_name // .model.id // "unknown"')
CWD=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // "unknown"')
COST=$(echo "$input" | jq -r '.cost.total_cost_usd // 0')
USED_PCT=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
REMAINING_PCT=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
DURATION_MS=$(echo "$input" | jq -r '.cost.total_duration_ms // 0')

# Derive used % from remaining if used not available
if [ -z "$USED_PCT" ] && [ -n "$REMAINING_PCT" ]; then
  USED_PCT=$(echo "$REMAINING_PCT" | awk '{printf "%d", 100 - $1}')
fi
USED_PCT=${USED_PCT:-0}
PCT=$(echo "$USED_PCT" | cut -d. -f1)

# Shorten path
HOME_DIR="$HOME"
SHORT_CWD="${CWD/#$HOME_DIR/\~}"

CYAN='\033[36m'; GREEN='\033[32m'; YELLOW='\033[33m'; RED='\033[31m'; RESET='\033[0m'

# Bar color based on usage
if [ "$PCT" -ge 90 ]; then BAR_COLOR="$RED"
elif [ "$PCT" -ge 70 ]; then BAR_COLOR="$YELLOW"
else BAR_COLOR="$GREEN"; fi

FILLED=$((PCT / 10)); EMPTY=$((10 - FILLED))
printf -v FILL "%${FILLED}s"; printf -v PAD "%${EMPTY}s"
BAR="[${FILL// /|}${PAD// /.}]"

MINS=$((DURATION_MS / 60000)); SECS=$(((DURATION_MS % 60000) / 1000))

BRANCH=""
git rev-parse --git-dir > /dev/null 2>&1 && BRANCH=" | 🌿 $(git branch --show-current 2>/dev/null)"

COST_FMT=$(printf '$%.4f' "$COST")

echo -e "${CYAN}[${MODEL}]${RESET} 📁 ${SHORT_CWD}${BRANCH}"
echo -e "${BAR_COLOR}${BAR}${RESET} ${PCT}% ctx | ${YELLOW}${COST_FMT}${RESET} | ⏱️ ${MINS}m ${SECS}s"
