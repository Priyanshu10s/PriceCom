from .models import WalletTransaction
import logging

logger = logging.getLogger(__name__)

def verify_transaction_integrity(tx_uuid: str) -> bool:
    """
    Cryptographic Verification:
    Re-calculates the SHA-256 HMAC for the stored transaction record.
    Returns True if intact, False if DB was manually tampered.
    """
    try:
        tx = WalletTransaction.objects.get(tx_uuid=tx_uuid)
        expected_hash = tx.calculate_integrity_hash()
        
        is_valid = (tx.security_hash == expected_hash)
        
        if not is_valid:
            logger.critical(f"TAMPERING DETECTED: Transaction {tx_uuid} compromised!")
            
        return is_valid
    except WalletTransaction.DoesNotExist:
        return False
