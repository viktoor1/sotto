#!/usr/bin/env python3
"""Read public issue and PR metadata; never post or use stored credentials."""
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

root = Path(__file__).resolve().parent / "activity"
stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
endpoints = {
    "issue": "https://api.github.com/repos/getsotto/sotto/issues/637",
    "comments": "https://api.github.com/repos/getsotto/sotto/issues/637/comments?per_page=100",
    "open-prs": "https://api.github.com/repos/getsotto/sotto/pulls?state=open&per_page=100",
}
failed = False
for name, url in endpoints.items():
    request = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json",
                                                   "User-Agent": "sotto-637-contribution-investigation"})
    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            payload = response.read()
            next_page = 'rel="next"' in response.headers.get("Link", "")
        target = root / f"{stamp}-{name}.json"
        target.write_bytes(payload)
        data = json.loads(payload)
        print(name, url, "saved:", target.name, "more pages:", next_page)
        if name == "issue":
            print(json.dumps({k: data.get(k) for k in ["title", "state", "updated_at", "html_url", "body"]}, indent=2))
            print("assignees:", [user["login"] for user in data.get("assignees", [])])
        elif name == "comments":
            for comment in data:
                print(json.dumps({"author": comment["user"]["login"], "date": comment["created_at"],
                                  "url": comment["html_url"], "body": comment["body"]}))
        else:
            print("Open PR titles (read-only review for possible competing work):")
            for pr in data:
                print(json.dumps({"number": pr["number"], "title": pr["title"], "url": pr["html_url"],
                                  "body": pr.get("body"), "author": pr["user"]["login"]}))
        if next_page:
            failed = True
            print("Additional pages need review before claiming completeness.")
    except (urllib.error.URLError, TimeoutError) as error:
        failed = True
        print(name, "read failed:", str(error))
raise SystemExit(1 if failed else 0)
