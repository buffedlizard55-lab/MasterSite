#!/usr/bin/env python3
"""Measure the real GitHub REST request cost and wall-clock of each read-only audit.

Run this from a *scratch copy* of the repository (never the real checkout — the
audits write `tools/last_*.json` when they finish):

    mkdir -p /tmp/measure && git clone . /tmp/measure/repo
    cp reports/scheduled-audit/raw/counting_shim/sitecustomize.py /tmp/measure/shim/
    cp reports/scheduled-audit/raw/measure_costs.py /tmp/measure/
    GITHUB_TOKEN=... python3 /tmp/measure/measure_costs.py /tmp/measure

Writes `count-<tool>.json` (one URL per request, query strings stripped),
`cost-<tool>.log` (the tool's own output) and `measure_costs.json` (the summary
committed next to this file for the 2026-10-11 measurement).
"""
import json
import os
import subprocess
import sys
import time

OUT_DIR = sys.argv[1] if len(sys.argv) > 1 else "."
REPO = os.path.join(OUT_DIR, "repo")
SHIM = os.path.join(OUT_DIR, "shim")
TOOLS = [
    ("audit_kind", ["python3", "tools/audit_kind.py"]),
    ("audit_descriptions", ["python3", "tools/audit_descriptions.py"]),
    ("verify_live", ["python3", "tools/verify_live.py"]),
    ("audit_provenance", ["python3", "tools/audit_provenance.py"]),
]

results = {"startedUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "tools": []}
for name, cmd in TOOLS:
    count_path = os.path.join(OUT_DIR, "count-%s.json" % name)
    env = dict(os.environ, PYTHONPATH=SHIM, COUNT_OUT=count_path)
    started = time.time()
    with open(os.path.join(OUT_DIR, "cost-%s.log" % name), "w", encoding="utf-8") as log:
        code = subprocess.run(cmd, cwd=REPO, stdout=log, stderr=subprocess.STDOUT,
                              env=env).returncode
    elapsed = round(time.time() - started, 1)
    calls = json.load(open(count_path, encoding="utf-8")) if os.path.exists(count_path) else []
    families = {}
    for url in calls:
        key = url.replace("https://api.github.com", "").split("/")
        key = "/".join(key[:5])
        families[key] = families.get(key, 0) + 1
    entry = {"tool": name, "exitCode": code, "seconds": elapsed, "requests": len(calls),
             "topEndpoints": sorted(families.items(), key=lambda kv: -kv[1])[:5]}
    results["tools"].append(entry)
    print(json.dumps(entry), flush=True)
results["finishedUtc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
results["totalRequests"] = sum(t["requests"] for t in results["tools"])
results["totalSeconds"] = sum(t["seconds"] for t in results["tools"])
json.dump(results, open(os.path.join(OUT_DIR, "measure_costs.json"), "w", encoding="utf-8"),
          indent=2)
print("TOTAL requests=%s seconds=%s" % (results["totalRequests"], results["totalSeconds"]),
      flush=True)
