#!/usr/bin/env python3
"""
Entry point for database query utility.
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from db_query import main

if __name__ == "__main__":
    main()
