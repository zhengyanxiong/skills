# Python Debugger (pdb + debugpy)

## Overview

Three tools: breakpoint()+pdb (local), python -m pdb (no edits), debugpy (remote/headless).
Start with breakpoint(). It is the cheapest thing that works.

## pdb Quick Reference

(Pdb) prompt: n/s/r/c/unt/j/l/w/u/d/a/p/pp/display/b/cl/tbreak/!/interact/q

## Recipe 1: Local breakpoint

Add breakpoint() in source, run normally. Remove before committing: rg -n breakpoint\(\) --type py

## Recipe 2: Launch under pdb (no source edits)

python -m pdb path/to/script.py arg1 arg2

## Recipe 3: Debug pytest test

scripts/run_tests.sh tests/path/to/test_file.py::test_name --pdb
Always add -p no:xdist since pdb does not work under xdist

## Recipe 4: Post-mortem

import pdb,sys; pdb.post_mortem(sys.exc_info()[2])

## Recipe 5: Remote debug with debugpy

source /home/bb/hermes-agent/.venv/bin/activate && pip install debugpy
Pattern A: source-edit with debugpy.listen + wait_for_client
Pattern B: python -m debugpy --listen 127.0.0.1:5678 --wait-for-client script.py
Pattern C: python -m debugpy --listen 127.0.0.1:5678 --pid <pid>
Best for terminal: pip install remote-pdb; set_trace(host, port); nc host port

## Hermes Debugging

tui_gateway: source-edit with debugpy.listen or use remote-pdb
_SlashWorker: remote-pdb set_trace() in the exec path
gateway/run.py: remote-pdb at a handler

## Common Pitfalls

1. pdb under pytest-xdist silently does nothing - use -p no:xdist or -n 0
2. PYTHONBREAKPOINT=0 disables all breakpoint() calls
3. debugpy.listen blocks only with wait_for_client()
4. Attach to PID fails on hardened kernels (ptrace_scope=1)
5. pdb only debugs current thread - use debugpy for multithreaded code
