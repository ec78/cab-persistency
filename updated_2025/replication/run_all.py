"""
run_all.py
==========
Single entry point for the full MNL replication.

Runs all four scripts in order:
  01_baseline_mnl.py          → Tables 4, 5, 6
  02_binary_logit.py          → Table 7
  03_subgroups.py             → Tables 8, 9
  04_lagged_er_robustness.py  → Table 6 (CV column) + Table 4a

Output files are written to the output/ directory.
Expected runtime: 2–5 minutes on a standard laptop.

Usage:
  python run_all.py
"""

import subprocess
import sys
import time
from pathlib import Path

SCRIPTS = [
    ("01_baseline_mnl.py",         "Tables 4, 5, 6  — Baseline MNLogit"),
    ("02_binary_logit.py",         "Table 7         — Binary logit robustness"),
    ("03_subgroups.py",            "Tables 8, 9     — Income & time-period subgroups"),
    ("04_lagged_er_robustness.py", "Table 6 (CV) + Table 4a — Lagged ER robustness"),
]

ROOT    = Path(__file__).resolve().parent
CODE    = ROOT / "code"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)

print("=" * 65)
print("CAB PERSISTENCY — MNL REPLICATION")
print("=" * 65)
print(f"Working directory : {ROOT}")
print(f"Output directory  : {OUT_DIR}")
print(f"Python executable : {sys.executable}")
print("=" * 65)

total_start = time.time()
results = []

for script_name, description in SCRIPTS:
    script_path = CODE / script_name
    print(f"\n[{'='*20}]")
    print(f"Running : {script_name}")
    print(f"Purpose : {description}")
    print(f"[{'='*20}]")

    start = time.time()
    proc  = subprocess.run(
        [sys.executable, str(script_path)],
        cwd=str(ROOT),
        capture_output=False,   # stream output to terminal
    )
    elapsed = time.time() - start

    status = "OK" if proc.returncode == 0 else f"FAILED (exit code {proc.returncode})"
    results.append((script_name, status, elapsed))
    print(f"\n  → {status} ({elapsed:.1f}s)")

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 65)
print("SUMMARY")
print("=" * 65)
all_ok = True
for script_name, status, elapsed in results:
    flag = "✓" if status == "OK" else "✗"
    print(f"  {flag}  {script_name:<40} {status}  ({elapsed:.1f}s)")
    if status != "OK":
        all_ok = False

total_elapsed = time.time() - total_start
print(f"\n  Total elapsed: {total_elapsed:.1f}s")

if all_ok:
    print("\nAll scripts completed successfully.")
    print(f"Output files written to: {OUT_DIR}")
    for f in sorted(OUT_DIR.glob("*.xlsx")):
        print(f"  {f.name}")
else:
    print("\nOne or more scripts failed. Check output above for error messages.")
    sys.exit(1)
