#!/usr/bin/env python3
"""Record issue-specific commands and output without collecting the environment."""
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--id", required=True)
parser.add_argument("--cwd", required=True)
parser.add_argument("command", nargs=argparse.REMAINDER)
args = parser.parse_args()
command = args.command[1:] if args.command[:1] == ["--"] else args.command
if not command:
    parser.error("a command is required after --")
if not args.id.replace("-", "").replace("_", "").isalnum():
    parser.error("id must contain only letters, numbers, hyphens or underscores")

logs = ROOT / "activity"
logs.mkdir(exist_ok=True)
started = datetime.now(timezone.utc)
log = logs / (started.strftime("%Y%m%dT%H%M%S%fZ") + "-" + args.id + ".log")
result = subprocess.run(command, cwd=args.cwd, stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT, text=True)
log.write_text(result.stdout)
entry = {"id": args.id, "startedAt": started.isoformat(),
         "finishedAt": datetime.now(timezone.utc).isoformat(),
         "cwd": args.cwd, "argv": command, "exitCode": result.returncode,
         "output": str(log.relative_to(ROOT))}
with (ROOT / "activity.jsonl").open("a") as stream:
    stream.write(json.dumps(entry) + "\n")
sys.stdout.write(result.stdout)
print(f"\nRecorded: {entry['output']} (exit {result.returncode})", flush=True)
sys.exit(result.returncode)
