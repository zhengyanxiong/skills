# Node.js Inspect Debugger

## Overview

When console.log is not enough, drive Node built-in V8 inspector from terminal. Real breakpoints, step in/over/out, call-stack walking, local/closure scope dumps.

Prefer node inspect first. It is always available and the REPL is fast.

## Quick Reference

Launch paused: node inspect path/to/script.js
node inspect: debug> prompt with c/cont/n/next/s/step/o/out/pause/sb/cb/bt/list/watch/repl/exec/restart/kill/.exit

## Attaching to Running Process

kill -SIGUSR1 <pid> then node inspect -p <pid>

## Hermes ui-tui Debugging

cd /home/bb/hermes-agent/ui-tui && npm run build && node --inspect-brk dist/entry.js
In another terminal: node inspect -p <node pid>

For running hermes --tui: kill -SIGUSR1 <tui_pid> then curl http://127.0.0.1:9229/json/list

## CDP Scripting

npm i -g chrome-remote-interface; node --inspect-brk=9229 target.js
Use /tmp/cdp-debug.js with chrome-remote-interface library

## Common Pitfalls

1. TS sourcemaps: breakpoints hit emitted JS, not .ts. Use dist/*.js or --enable-source-maps
2. --inspect vs --inspect-brk: latter pauses before first line
3. Port 9229 collisions: use --inspect=0 for random port
4. Child processes: NODE_OPTIONS=--inspect-brk propagates to all children
5. Security: --inspect=0.0.0.0:9229 exposes arbitrary code execution
