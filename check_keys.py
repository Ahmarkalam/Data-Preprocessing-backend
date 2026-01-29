
from src.database.connection import SessionLocal
from src.database.models import Client

def list_clients():
    db = SessionLocal()
    try:
        clients = db.query(Client).all()
        print(f"Found {len(clients)} clients:")
        for client in clients:
            print(f"ID:: {client.id}")
            print(f"Name: {client.name}")
            print(f"API Key: {client.api_key}")
            print("-" * 30)
    finally:
        db.close()

if __name__ == "__main__":
    list_clients()
