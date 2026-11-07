#!/bin/sh
for p in /proc/[0-9]*; do
  pid=$(basename "$p")
  cmd=$(tr "\0" " " < "$p/cmdline" 2>/dev/null)
  case "$cmd" in
    *bench_helper*)
      echo "KILL $pid: $cmd"
      kill -9 "$pid" 2>/dev/null
      ;;
  esac
done
echo "--- cleanup done ---"
