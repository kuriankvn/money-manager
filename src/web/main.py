"""CLI entry point for Streamlit UI"""
import sys
import os
from pathlib import Path


def main():
    """Launch Streamlit UI"""
    home_path = Path(__file__).parent / "Home.py"
    os.execvp("streamlit", ["streamlit", "run", str(home_path)])


if __name__ == "__main__":
    main()
