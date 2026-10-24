#!/usr/bin/env python3
"""Check the unrelated timeout on unchanged upstream; restore our exact work."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
repo = Path("/workspace/sotto")
paths = ["web/src/PayerTransferStart.tsx", "web/src/__tests__/PayerTransferJourneys.test.tsx"]
original = {p: (repo / p).read_bytes() for p in paths}
baseline = {p: subprocess.check_output(["git", "show", "HEAD:" + p], cwd=repo) for p in paths}
for path, contents in original.items():
    target = root / "baseline-probe-backup" / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(contents)
try:
    for path, contents in baseline.items():
        (repo / path).write_bytes(contents)
    subprocess.run(["git", "diff", "--exit-code"], cwd=repo, check=True)
    print("Confirmed clean upstream before the baseline test.", flush=True)
    result = subprocess.run(
        ["bash", "-c", "source /workspace/.setup/sotto-env.sh\n"
         "npm test -- --maxWorkers=1 src/__tests__/base64.test.tsx"],
        cwd=repo / "web", text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
finally:
    for path, contents in baseline.items():
        if (repo / path).read_bytes() != contents:
            raise RuntimeError("File changed during baseline check; refusing to overwrite it: " + path)
    for path, contents in original.items():
        (repo / path).write_bytes(contents)
print(result.stdout)
report = {"sourceCommit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip(),
          "cleanUpstreamVerified": True, "runnerExitCode": result.returncode,
          "sameTimeoutObserved": result.returncode == 1 and "Test timed out in 15000ms" in result.stdout,
          "repairRestored": all((repo / p).read_bytes() == data for p, data in original.items()),
          "restoredHashes": {p: hashlib.sha256(data).hexdigest() for p, data in original.items()}}
(root / "upstream-baseline-probe.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2))
if not report["repairRestored"] or not report["sameTimeoutObserved"]:
    raise SystemExit("Baseline result needs further investigation")
