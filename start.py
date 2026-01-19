"""
Simple script to start the API server
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("  DATA PREPROCESSING API")
    print("="*60)
    print("\n📍 API Server: http://localhost:8000")
    print("📚 Documentation: http://localhost:8000/docs")
    print("📖 ReDoc: http://localhost:8000/redoc")
    print("\nPress CTRL+C to stop the server\n")
    print("="*60 + "\n")
    
    try:
        uvicorn.run(
            "src.api.main:app",
            host="127.0.0.1",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n\n👋 Server stopped. Goodbye!")