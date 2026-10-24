#!/usr/bin/env python3
"""Publish the authorised investigation files without changing the code branch."""
import json
import shutil
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent
code_repo = Path("/workspace/sotto")
branch = "evidence/637-investigation"
remote = "https://github.com/viktoor1/sotto.git"

def run(args, cwd, capture=False):
    print("Running:", *args, flush=True)
    return subprocess.run(args, cwd=cwd, check=True, text=True,
                          stdout=subprocess.PIPE if capture else None)

name = subprocess.check_output(["git", "config", "user.name"], cwd=code_repo, text=True).strip()
email = subprocess.check_output(["git", "config", "user.email"], cwd=code_repo, text=True).strip()
existing = subprocess.check_output(["git", "ls-remote", "--heads", remote, "refs/heads/" + branch], cwd=code_repo, text=True).strip()
with tempfile.TemporaryDirectory(prefix="sotto-637-evidence-", dir="/tmp") as directory:
    dest = Path(directory)
    if existing:
        report_path = root / "evidence-publication.json"
        assert report_path.is_file(), "Existing evidence branch needs inspection"
        previous = json.loads(report_path.read_text())
        assert existing.split()[0] == previous["commit"], "Remote evidence changed; do not overwrite it"
        run(["git", "clone", "--depth", "1", "--branch", branch, remote, str(dest)], code_repo)
    else:
        run(["git", "init", "-b", branch], dest)
        run(["git", "remote", "add", "origin", remote], dest)
    run(["git", "config", "user.name", name], dest)
    run(["git", "config", "user.email", email], dest)
    count = 0
    for source in sorted(root.rglob("*")):
        if not source.is_file() or "__pycache__" in source.parts:
            continue
        assert not source.is_symlink()
        relative = source.relative_to(root)
        assert ".git" not in relative.parts
        target = dest / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        count += 1
    print("Issue-specific evidence files copied:", count, flush=True)
    run(["git", "add", "--all"], dest)
    # Raw HTML, captured output and patch files retain their exact original bytes,
    # including meaningful patch-context spaces. Check the authored entry pages.
    run(["git", "diff", "--cached", "--check", "--", "README.md", "repair-review.md",
         "discovery-path.md", "pr-body.md", "publish-evidence.py"], dest)
    run(["git", "commit", "--signoff", "-m", "docs: record Sotto #637 investigation and verification"], dest)
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=dest, text=True).strip()
    run(["git", "push", "--set-upstream", "origin", "HEAD:refs/heads/" + branch], dest)
    actual = subprocess.check_output(["git", "ls-remote", "--heads", "origin", "refs/heads/" + branch], cwd=dest, text=True).split()[0]
    assert actual == commit
report = {"publishedAt": datetime.now(timezone.utc).isoformat(), "branch": branch,
          "commit": commit, "fileCount": count,
          "url": "https://github.com/viktoor1/sotto/tree/" + branch,
          "codeCommit": "e879c71f0e5a5d1b9e3d1219a89f80e7c5c040b8",
          "scope": "authorised issue-specific documentation, HTML, journal and evidence only"}
(root / "evidence-publication.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report, indent=2), flush=True)
