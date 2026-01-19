
"""
Reset database - WARNING: This will delete all data!
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import drop_db, init_db
from src.utils.logger import get_logger

logger = get_logger("reset_db")

def main():
    """Reset database"""
    print("\n" + "="*60)
    print("    DATABASE RESET WARNING  ")
    print("="*60 + "\n")
    print("This will DELETE ALL DATA in the database!")
    print("This action CANNOT be undone!\n")
    
    confirm = input("Type 'RESET' to confirm: ")
    
    if confirm != "RESET":
        print("\n Reset cancelled.\n")
        sys.exit(0)
    
    try:
        logger.warning("Dropping all database tables...")
        drop_db()
        print(" All tables dropped")
        
        logger.info("Recreating database tables...")
        init_db()
        print(" Database recreated")
        
        print("\n Database reset complete!\n")
        print("You can now create new clients using:")
        print("  python scripts/manage_clients.py create <client_id> <name> <email>\n")
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")
        print(f"\n Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()