"""Run the synthetic demo and print its measured numbers."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from environmental_monitoring.pipeline import run_demo

if __name__ == "__main__":
    for key, value in run_demo().items():
        print(f"{key}={value}")
