#!/usr/bin/env python
"""Launch DevMetrics Dashboard."""

import subprocess
import sys
from pathlib import Path

def main():
    """Run the Streamlit app."""
    app_path = Path(__file__).parent / "app.py"
    
    print("🚀 Starting DevMetrics Dashboard...")
    print(f"📁 App: {app_path}")
    print("🌐 Open browser at: http://localhost:8501")
    print("\n" + "="*50)
    
    subprocess.run([
        sys.executable, "-m", "streamlit", "run",
        str(app_path),
        "--server.headless", "true"
    ])

if __name__ == "__main__":
    main()
