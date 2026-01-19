
"""
Quick setup script for new installations
"""
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_db
from src.database.crud import create_client
from src.database import get_db
from src.utils.logger import get_logger
from config.settings import settings

logger = get_logger("quick_setup")

def main():
    """Quick setup for first-time users"""
    print("\n" + "="*60)
    print("  DATA PREPROCESSING BACKEND - QUICK SETUP")
    print("="*60 + "\n")
    
    print(" Step 1: Creating directories...")
    try:
        settings.create_directories()
        print(" Directories created\n")
    except Exception as e:
        print(f" Error creating directories: {e}")
        sys.exit(1)
    
    print("🗄️  Step 2: Initializing database...")
    try:
        init_db()
        print(" Database initialized\n")
    except Exception as e:
        print(f" Error initializing database: {e}")
        sys.exit(1)
    
    
    print(" Step 3: Creating demo client account...")
    print("\nPlease enter demo client details:")
    
    client_id = input("  Client ID (e.g., demo_client): ").strip() or "demo_client"
    name = input("  Name (e.g., Demo User): ").strip() or "Demo User"
    email = input("  Email (e.g., demo@example.com): ").strip() or "demo@example.com"
    company = input("  Company (optional): ").strip() or None
    
    print("\nSelect plan:")
    print("  1. Free (1 GB/month)")
    print("  2. Basic (10 GB/month)")
    print("  3. Premium (100 GB/month)")
    plan_choice = input("  Choice [1]: ").strip() or "1"
    
    plan_map = {"1": "free", "2": "basic", "3": "premium"}
    plan = plan_map.get(plan_choice, "free")
    
    try:
        with get_db() as db:
            client = create_client(
                db=db,
                client_id=client_id,
                name=name,
                email=email,
                company=company,
                plan_type=plan
            )
            # Extract all values while session is still open
            api_key = client.api_key
            client_plan = client.plan_type
            quota = client.monthly_quota_mb
        
        print("\n✅ Demo client created successfully!\n")
        print("="*60)
        print("CLIENT CREDENTIALS")
        print("="*60)
        print(f"Client ID:  {client_id}")
        print(f"API Key:    {api_key}")
        print(f"Plan:       {client_plan}")
        print(f"Quota:      {quota} MB/month")
        print("="*60)
        print("\n⚠️  IMPORTANT: Save the API key - you'll need it for authentication!\n")
        
    except ValueError as e:
        print(f"\n Error: {e}")
        print("   Client might already exist. Use a different client_id.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n Error creating client: {e}\n")
        sys.exit(1)
    
    
    print(" Setup complete! Next steps:\n")
    print("1. Start the API server:")
    print("   python start.py\n")
    print("2. Visit the API documentation:")
    print("   http://localhost:8000/docs\n")
    print("3. Test the API with your credentials:")
    print("   curl -H 'X-API-Key: YOUR_API_KEY' http://localhost:8000/jobs/\n")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()