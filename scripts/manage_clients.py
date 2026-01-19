
"""
CLI tool for managing clients
"""
import sys
from pathlib import Path
import argparse

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import get_db
from src.database.crud import (
    create_client, get_client, list_clients, 
    update_client, delete_client, reset_monthly_quota
)
from src.utils.logger import get_logger

logger = get_logger("manage_clients")

def create_client_cmd(args):
    """Create a new client"""
    print(f"\n🔨 Creating client: {args.client_id}")
    
    with get_db() as db:
        try:
            client = create_client(
                db=db,
                client_id=args.client_id,
                name=args.name,
                email=args.email,
                company=args.company,
                plan_type=args.plan
            )
            
            print(f"\n✅ Client created successfully!")
            print(f"\n{'='*60}")
            print(f"Client ID:      {client.id}")
            print(f"Name:           {client.name}")
            print(f"Email:          {client.email}")
            print(f"Company:        {client.company or 'N/A'}")
            print(f"Plan:           {client.plan_type}")
            print(f"Monthly Quota:  {client.monthly_quota_mb} MB")
            print(f"API Key:        {client.api_key}")
            print(f"{'='*60}\n")
            
            print("⚠️  IMPORTANT: Save the API key securely!")
            print("   It will be needed for authentication.\n")
            
        except ValueError as e:
            print(f" Error: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to create client: {e}")
            print(f" Error: {e}")
            sys.exit(1)

def list_clients_cmd(args):
    """List all clients"""
    print("\n Listing clients...\n")
    
    with get_db() as db:
        try:
            clients = list_clients(db, skip=0, limit=args.limit)
            
            if not clients:
                print("No clients found.")
                return
            
            print(f"{'='*100}")
            print(f"{'Client ID':<20} {'Name':<25} {'Email':<30} {'Plan':<10} {'Active':<8}")
            print(f"{'='*100}")
            
            for client in clients:
                print(f"{client.id:<20} {client.name:<25} {client.email:<30} {client.plan_type:<10} {'Yes' if client.is_active else 'No':<8}")
            
            print(f"{'='*100}")
            print(f"\nTotal: {len(clients)} client(s)\n")
            
        except Exception as e:
            logger.error(f"Failed to list clients: {e}")
            print(f" Error: {e}")
            sys.exit(1)

def get_client_cmd(args):
    """Get client details"""
    print(f"\n🔍 Getting details for client: {args.client_id}\n")
    
    with get_db() as db:
        try:
            client = get_client(db, args.client_id)
            
            if not client:
                print(f" Client not found: {args.client_id}")
                sys.exit(1)
            
            from src.database.crud import get_client_job_count, get_client_completed_jobs, get_monthly_usage_summary
            
            total_jobs = get_client_job_count(db, args.client_id)
            completed_jobs = get_client_completed_jobs(db, args.client_id)
            usage = get_monthly_usage_summary(db, args.client_id)
            
            print(f"{'='*60}")
            print(f"CLIENT DETAILS")
            print(f"{'='*60}")
            print(f"Client ID:        {client.id}")
            print(f"Name:             {client.name}")
            print(f"Email:            {client.email}")
            print(f"Company:          {client.company or 'N/A'}")
            print(f"Plan:             {client.plan_type}")
            print(f"Status:           {'Active' if client.is_active else 'Inactive'}")
            print(f"Created:          {client.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"\n{'='*60}")
            print(f"QUOTA & USAGE")
            print(f"{'='*60}")
            print(f"Monthly Quota:    {client.monthly_quota_mb} MB")
            print(f"Used:             {client.used_quota_mb:.2f} MB ({(client.used_quota_mb/client.monthly_quota_mb*100):.1f}%)")
            print(f"Remaining:        {(client.monthly_quota_mb - client.used_quota_mb):.2f} MB")
            print(f"\n{'='*60}")
            print(f"STATISTICS")
            print(f"{'='*60}")
            print(f"Total Jobs:       {total_jobs}")
            print(f"Completed Jobs:   {completed_jobs}")
            print(f"Success Rate:     {(completed_jobs/total_jobs*100):.1f}%" if total_jobs > 0 else "N/A")
            print(f"\n{'='*60}")
            print(f"MONTHLY USAGE")
            print(f"{'='*60}")
            print(f"Data Processed:   {usage['total_data_mb']:.2f} MB")
            print(f"Jobs This Month:  {usage['total_jobs']}")
            print(f"Processing Time:  {usage['total_processing_time_seconds']:.2f} seconds")
            print(f"{'='*60}\n")
            
            if args.show_api_key:
                print(f"API Key:          {client.api_key}\n")
            else:
                print("💡 Use --show-api-key to display the API key\n")
            
        except Exception as e:
            logger.error(f"Failed to get client: {e}")
            print(f" Error: {e}")
            sys.exit(1)

def update_client_cmd(args):
    """Update client details"""
    print(f"\n  Updating client: {args.client_id}\n")
    
    with get_db() as db:
        try:
            client = update_client(
                db=db,
                client_id=args.client_id,
                name=args.name,
                email=args.email,
                company=args.company,
                plan_type=args.plan,
                is_active=args.active if args.active is not None else None
            )
            
            if not client:
                print(f" Client not found: {args.client_id}")
                sys.exit(1)
            
            print(f"✅ Client updated successfully!")
            print(f"\nUpdated details:")
            print(f"  Name:     {client.name}")
            print(f"  Email:    {client.email}")
            print(f"  Company:  {client.company or 'N/A'}")
            print(f"  Plan:     {client.plan_type}")
            print(f"  Status:   {'Active' if client.is_active else 'Inactive'}\n")
            
        except Exception as e:
            logger.error(f"Failed to update client: {e}")
            print(f" Error: {e}")
            sys.exit(1)

def delete_client_cmd(args):
    """Delete a client"""
    print(f"\n  WARNING: This will delete client '{args.client_id}' and ALL associated data!")
    
    if not args.force:
        confirm = input("Type 'DELETE' to confirm: ")
        if confirm != "DELETE":
            print("❌ Deletion cancelled.")
            return
    
    with get_db() as db:
        try:
            success = delete_client(db, args.client_id)
            
            if not success:
                print(f" Client not found: {args.client_id}")
                sys.exit(1)
            
            print(f"✅ Client deleted successfully: {args.client_id}\n")
            
        except Exception as e:
            logger.error(f"Failed to delete client: {e}")
            print(f" Error: {e}")
            sys.exit(1)

def reset_quota_cmd(args):
    """Reset client's monthly quota"""
    print(f"\n🔄 Resetting quota for client: {args.client_id}\n")
    
    with get_db() as db:
        try:
            client = reset_monthly_quota(db, args.client_id)
            
            if not client:
                print(f" Client not found: {args.client_id}")
                sys.exit(1)
            
            print(f"✅ Quota reset successfully!")
            print(f"   Monthly Quota: {client.monthly_quota_mb} MB")
            print(f"   Used: {client.used_quota_mb} MB\n")
            
        except Exception as e:
            logger.error(f"Failed to reset quota: {e}")
            print(f" Error: {e}")
            sys.exit(1)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Client Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Create client
    create_parser = subparsers.add_parser('create', help='Create a new client')
    create_parser.add_argument('client_id', help='Unique client ID')
    create_parser.add_argument('name', help='Client name')
    create_parser.add_argument('email', help='Client email')
    create_parser.add_argument('--company', help='Company name', default=None)
    create_parser.add_argument('--plan', choices=['free', 'basic', 'premium'], default='free', help='Plan type')
    create_parser.set_defaults(func=create_client_cmd)
    
    # List clients
    list_parser = subparsers.add_parser('list', help='List all clients')
    list_parser.add_argument('--limit', type=int, default=100, help='Maximum number of clients to show')
    list_parser.set_defaults(func=list_clients_cmd)
    
    # Get client
    get_parser = subparsers.add_parser('get', help='Get client details')
    get_parser.add_argument('client_id', help='Client ID')
    get_parser.add_argument('--show-api-key', action='store_true', help='Show API key')
    get_parser.set_defaults(func=get_client_cmd)
    
    # Update client
    update_parser = subparsers.add_parser('update', help='Update client details')
    update_parser.add_argument('client_id', help='Client ID')
    update_parser.add_argument('--name', help='New name')
    update_parser.add_argument('--email', help='New email')
    update_parser.add_argument('--company', help='New company')
    update_parser.add_argument('--plan', choices=['free', 'basic', 'premium'], help='New plan')
    update_parser.add_argument('--active', type=bool, help='Set active status (True/False)')
    update_parser.set_defaults(func=update_client_cmd)
    
    # Delete client
    delete_parser = subparsers.add_parser('delete', help='Delete a client')
    delete_parser.add_argument('client_id', help='Client ID')
    delete_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    delete_parser.set_defaults(func=delete_client_cmd)
    
    # Reset quota
    quota_parser = subparsers.add_parser('reset-quota', help='Reset monthly quota')
    quota_parser.add_argument('client_id', help='Client ID')
    quota_parser.set_defaults(func=reset_quota_cmd)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)

if __name__ == "__main__":
    main()