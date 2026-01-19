
""""
Initialize the database and create tables
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db, drop_db
from src.utils.logger import get_logger

logger = get_logger("init_db")

def main():
    """Initialize database"""
    print("\n" + "="*60)
    print("  DATABASE INITIALIZATION")
    print("="*60 + "\n")
    
    try:
        logger.info("Creating database tables...")
        init_db()
        print("✅ Database initialized successfully!")
        print("\nTables created:")
        print("  - clients")
        print("  - jobs")
        print("  - quality_metrics")
        print("  - usage_logs")
        print("  - api_keys")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        print(f" Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()