"""Print demo numbers from a real run (used to fill in the README)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from environmental_monitoring.pipeline import run_demo

if __name__ == "__main__":
    for key, value in run_demo().items():
        print(f"{key}={value}")
