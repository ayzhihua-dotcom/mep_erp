#!/bin/sh
for p in /proc/[0-9]*; do
  pid=$(basename "$p")
  cmd=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null)
  ppid=$(grep -m1 '^PPid:' "$p/status" 2>/dev/null | cut -d' ' -f2)
  state=$(grep -m1 '^State:' "$p/status" 2>/dev/null | cut -d' ' -f2)
  case "$cmd" in
    *console*|*frappe-bench*) echo "PID=$pid PPID=$ppid STATE=$state CMD=$cmd" ;;
  esac
done
