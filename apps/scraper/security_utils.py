
import hmac
import hashlib
import json
from django.conf import settings
from decimal import Decimal

def generate_signature(secret_key, data_dict):
    """
    Generates HMAC-SHA256 signature for a dictionary of data.
    """
    # Sort keys to ensure consistent serialization
    serialized_data = json.dumps(data_dict, sort_keys=True, default=str)
    signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=serialized_data.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature

def verify_signature(secret_key, data_dict, signature):
    """
    Verifies the signature of the data.
    """
    expected_signature = generate_signature(secret_key, data_dict)
    return hmac.compare_digest(expected_signature, signature)
