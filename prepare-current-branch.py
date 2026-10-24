#!/usr/bin/env python3
"""Preserve the reviewed work and carry it onto the fetched upstream main."""
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

repo = Path("/workspace/sotto")
root = Path(__file__).resolve().parent
component = "web/src/PayerTransferStart.tsx"
tests = "web/src/__tests__/PayerTransferJourneys.test.tsx"
branch = "fix/637-administrator-retry"

def git(*args):
    return subprocess.check_output(["git", *args], cwd=repo, text=True)

old = git("rev-parse", "HEAD").strip()
upstream = git("rev-parse", "FETCH_HEAD").strip()
assert old == "07f32e5cbdc758ddebfbc8a431302b93d2daa98a"
assert set(git("diff", "--name-only").splitlines()) == {component, tests}
assert not git("ls-files", "--others", "--exclude-standard").strip()
assert not git("branch", "--list", branch).strip()
ours = {path: (repo / path).read_text() for path in [component, tests]}
theirs = {path: git("show", f"{upstream}:{path}") for path in ours}
base = git("show", f"{old}:{component}")

def chooser(text):
    return text[text.index("  async function chooseOrganisation("):text.index("  async function requestQuote(")]

assert chooser(theirs[component]) == chooser(base), "Upstream member discovery needs a new review"
personal, sponsored = theirs[component].split("export function SponsoredTransferStart", 1)
needle = '  const [error, setError] = useState<string | null>(null);\n'
assert personal.count(needle) == 1
personal = personal.replace(needle, needle +
    '  const [membersError, setMembersError] = useState<string | null>(null);\n'
    '  const [membersLoading, setMembersLoading] = useState(false);\n')
needle = '  const idempotencyKey = useRef<string | null>(null);\n'
assert personal.count(needle) == 1
personal = personal.replace(needle, needle +
    '  const membersInFlight = useRef(false);\n'
    '  const formBusy = busy || membersLoading;\n')
personal = personal.replace(chooser(personal), chooser(ours[component]))
assert personal.count('disabled={busy}') == 4
personal = personal.replace('disabled={busy}', 'disabled={formBusy}')
needle = 'disabled={busy || destinationOrgId === "" || counterpartyId === ""}'
assert personal.count(needle) == 1
personal = personal.replace(needle, needle.replace('busy ||', 'formBusy ||'))
recovery = ours[component][ours[component].index('    {membersError !== null'):ours[component].index('    {error !== null && <p role="alert">')]
error_line = '      {error !== null && <p role="alert">{error}</p>}\n'
assert personal.count(error_line) == 1
personal = personal.replace(error_line, ''.join('  ' + line + '\n' for line in recovery.splitlines()) + error_line)
updated = {component: personal + "export function SponsoredTransferStart" + sponsored}

start = ours[tests].index('  it("retries administrator loading for the selected organisation')
anchor = '  it("does not claim a second payer must accept when the caller can authorise both sides"'
regressions = ours[tests][start:ours[tests].index(anchor)]
assert theirs[tests].count(anchor) == 1
assert 'function deferred<T>()' in theirs[tests]
assert '{ act, cleanup,' in theirs[tests]
updated[tests] = theirs[tests].replace(anchor, regressions + anchor)

archive = root / ("before-upstream-update-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
archive.mkdir()
for group, contents in [("ours", ours), ("upstream", theirs), ("prepared", updated)]:
    for path, text in contents.items():
        target = archive / group / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
patch = subprocess.check_output(["git", "diff", "--binary"], cwd=repo)
(archive / "original-base-repair.patch").write_bytes(patch)
metadata = {"oldBranch": git("branch", "--show-current").strip(), "oldHead": old,
            "newBranch": branch, "upstreamMain": upstream,
            "originalWorkHashes": {p: hashlib.sha256(t.encode()).hexdigest() for p, t in ours.items()},
            "patchSha256": hashlib.sha256(patch).hexdigest()}
(archive / "preservation.json").write_text(json.dumps(metadata, indent=2) + "\n")
for path, text in ours.items():
    assert (archive / "ours" / path).read_text() == text
    assert (repo / path).read_text() == text
print("Verified recoverable copies of both edited files and the exact patch:", archive, flush=True)

for args in [("restore", "--", component, tests), ("switch", "-c", branch, upstream)]:
    print("Running:", "git", *args, flush=True)
    subprocess.run(["git", *args], cwd=repo, check=True)
for path, text in updated.items():
    (repo / path).write_text(text)
assert (repo / component).read_text().split("export function SponsoredTransferStart", 1)[1] == sponsored
print(git("status", "--short", "--branch"))
print(git("diff", "--stat"))
subprocess.run(["git", "diff", "--check"], cwd=repo, check=True)
print("Preserved upstream initial-discovery code and tests; no commit or push made.")
