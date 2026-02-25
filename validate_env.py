
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def validate_environment():
    """
    Antigravity Environment Validator.
    Ensures the 'Vault' is secure and the 'Bridge' is functional.
    """
    print("--- Antigravity Environment Check ---")
    
    # 1. Check .env existence
    env_path = Path('.env')
    if not env_path.exists():
        print("[FAIL] .env file not found!")
        sys.exit(1)
    print("[PASS] .env file exists.")
    
    # 2. Load Environment
    load_dotenv()
    
    # 3. Validate Critical Secrets
    secret_key = os.getenv('DJANGO_SECRET_KEY')
    if not secret_key or secret_key.startswith('django-insecure'):
        print("[FAIL] DJANGO_SECRET_KEY is missing or insecure!")
        sys.exit(1)
    print("[PASS] DJANGO_SECRET_KEY is set and secure.")
    
    # 4. Validate Portability
    db_url = os.getenv('DATABASE_URL')
    use_sqlite = os.getenv('USE_SQLITE')
    
    if not db_url and not use_sqlite:
        print("[FAIL] Neither DATABASE_URL nor USE_SQLITE is set!")
        sys.exit(1)
    print(f"[PASS] Database Configuration Found. (URL: {'Yes' if db_url else 'No'}, SQLite: {use_sqlite})")
    
    # 5. Validate Broker
    broker = os.getenv('CELERY_BROKER_URL')
    if not broker:
        print("[FAIL] CELERY_BROKER_URL is missing!")
        sys.exit(1)
    print("[PASS] Celery Broker Configured.")
    
    print("--- System Ready for Launch ---")

if __name__ == "__main__":
    validate_environment()
