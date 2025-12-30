"""Streamlit application entry point."""
import sys
from pathlib import Path


def run_app():
    """Entry point for money-manager-web script"""
    from streamlit.web import cli as stcli
    
    # Get the path to Home.py
    home_path = Path(__file__).parent / "Home.py"
    
    sys.argv = ["streamlit", "run", str(home_path)]
    sys.exit(stcli.main())

# Made with Bob
