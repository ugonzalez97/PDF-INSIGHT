#!/usr/bin/env python3
"""
Reset database utility - Deletes the SQLite database file.
WARNING: This will delete all processed PDF metadata!
"""
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import config


def reset_database():
    """Delete the database file."""
    db_file = config.DATABASE_FILE
    
    if not db_file.exists():
        print(f"✓ Database file does not exist: {db_file}")
        return
    
    # Ask for confirmation
    print(f"⚠️  WARNING: This will delete the database file:")
    print(f"   {db_file}")
    print(f"\n   All PDF metadata will be lost!")
    
    response = input("\nAre you sure? Type 'yes' to confirm: ")
    
    if response.lower() == 'yes':
        db_file.unlink()
        print(f"\n✓ Database deleted successfully!")
        print(f"  Next run of main.py will create a fresh database.")
    else:
        print("\n✗ Operation cancelled.")


if __name__ == "__main__":
    reset_database()
