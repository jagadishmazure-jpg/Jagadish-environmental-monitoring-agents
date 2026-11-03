"""Print the collected test count (CI docs check uses this)."""

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
env = dict(os.environ)
env["PYTHONPATH"] = str(ROOT / "src") + os.pathsep + env.get("PYTHONPATH", "")

out = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
    capture_output=True, text=True, check=True, cwd=ROOT, env=env,
)
lines = [line for line in out.stdout.splitlines() if "::" in line]
print(f"tests_collected={len(lines)}")
