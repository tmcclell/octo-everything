#!/usr/bin/env python3
"""Docker entrypoint: collect live data if configured, then launch Streamlit."""

import os
import subprocess
import sys


def main():
    use_dummy = os.getenv("USE_DUMMY_DATA", "true").lower()

    if use_dummy in ("false", "0", "no"):
        print("📡 Collecting live data from GitHub APIs...")
        result = subprocess.run([sys.executable, "collect_live_data.py"])
        if result.returncode != 0:
            print("⚠️  Live collection had errors — falling back to existing data")
    else:
        print("🎲 Using dummy data")

    os.execvp("streamlit", [
        "streamlit", "run", "app.py",
        "--server.port=8501", "--server.address=0.0.0.0",
    ])


if __name__ == "__main__":
    main()
