#!/usr/bin/env python3
"""
Backup database utility - Creates a timestamped backup of the database.
"""
import sys
from pathlib import Path
from datetime import datetime
import shutil

# Add src directory to Python path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import config


def backup_database():
    """Create a backup of the database."""
    db_file = config.DATABASE_FILE
    
    if not db_file.exists():
        print(f"✗ Database file does not exist: {db_file}")
        return
    
    # Create backup directory
    backup_dir = config.BASE_DIR / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    # Generate backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"pdf_insight_{timestamp}.db"
    
    # Copy database
    shutil.copy2(db_file, backup_file)
    
    # Get file sizes
    original_size = db_file.stat().st_size
    backup_size = backup_file.stat().st_size
    
    print(f"✓ Database backed up successfully!")
    print(f"  Original: {db_file} ({original_size:,} bytes)")
    print(f"  Backup:   {backup_file} ({backup_size:,} bytes)")
    
    # List all backups
    backups = sorted(backup_dir.glob("pdf_insight_*.db"))
    if len(backups) > 1:
        print(f"\n  Total backups: {len(backups)}")


if __name__ == "__main__":
    backup_database()
