#!/usr/bin/env python3
"""Negative control: prove the rapid-click regression detects a missing lock."""
import hashlib
import json
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parent
source = Path("/workspace/sotto/web/src/PayerTransferStart.tsx")
original = source.read_text()
guard = 'if (orgId === "" || membersInFlight.current) return;'
assert original.count(guard) == 1
mutant = original.replace(guard, 'if (orgId === "") return;')
try:
    source.write_text(mutant)
    result = subprocess.run(
        ["bash", "-c", "source /workspace/.setup/sotto-env.sh\n"
         "npm test -- --maxWorkers=1 src/__tests__/PayerTransferJourneys.test.tsx "
         "-t 'keeps administrator retry single-flight'"],
        cwd="/workspace/sotto/web", text=True,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
    )
finally:
    if source.read_text() != mutant:
        raise RuntimeError("Source changed during the probe; refusing to overwrite it")
    source.write_text(original)

print(result.stdout)
print("Controlled negative-check runner exit:", result.returncode)
print("Production source restored:", source.read_text() == original)
report = {
    "scope": "temporary removal of the loadMembers overlap guard only",
    "runnerExitCode": result.returncode,
    "productionSourceRestored": source.read_text() == original,
    "productionSourceSha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "detected": result.returncode == 1 and "called 2 times, but got 3 times" in result.stdout,
}
(root / "request-lock-probe.json").write_text(json.dumps(report, indent=2) + "\n")
if not report["detected"]:
    raise SystemExit("The negative control did not fail for the expected duplicate-request reason")
print("VERIFIED: rapid clicks cause three calls when the loader guard is removed; the regression detects it.")
