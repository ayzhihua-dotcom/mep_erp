#!/bin/sh
pkill -9 -f bench 2>/dev/null
pkill -9 -f python 2>/dev/null
sleep 3
for p in /proc/[0-9]*; do
  c=$(tr '\0' ' ' < "$p/cmdline" 2>/dev/null | cut -c1-70)
  if [ -n "$c" ]; then
    echo "$(basename $p): $c"
  fi
done
