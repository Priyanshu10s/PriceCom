import hashlib
from typing import Optional
from decimal import Decimal
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db import transaction, IntegrityError
from .models import Wallet, WalletTransaction
from django.conf import settings

class SecurityAlert(Exception):
    """Raised when fraudulent activity is detected."""
    pass

class WalletLedgerService:
    """
    High-Integrity Wallet Ledger Engine.
    Implements strict Atomic Database Transactions, Row-Level Locks, 
    and Cryptographic Verification to prevent double-spending and tampering.
    """

    @classmethod
    def get_or_create_wallet(cls, user_id: int) -> Wallet:
        """Returns the user wallet or creates one safely."""
        wallet, _ = Wallet.objects.get_or_create(user_id=user_id)
        return wallet

    @classmethod
    def record_transaction(
        cls, 
        user_id: int, 
        amount: Decimal, 
        tx_type: str, 
        category: str, 
        idempotency_key: str, 
        metadata: Optional[dict] = None
    ) -> WalletTransaction:
        """
        The Atomic Guard (execute_transaction / process_ledger_entry).
        Handles full transactional logic, rolling back cleanly if criteria fail.
        """
        if amount <= 0:
            raise ValidationError("Transaction amount must be strictly greater than 0.")
            
        if tx_type not in ['CREDIT', 'DEBIT']:
            raise ValidationError("Invalid transaction type.")

        try:
            # Row-Level Locking: Select_for_update blocks concurrent transactions from 
            # modifying this exact row until the atomic block commits or rolls back.
            with transaction.atomic():
                wallet = Wallet.objects.select_for_update().get(user_id=user_id)

                if wallet.status != 'ACTIVE':
                    raise ValidationError(f"Wallet is currently {wallet.status}.")

                # Concurrency Control / Idempotency Guard
                if WalletTransaction.objects.filter(idempotency_key=idempotency_key).exists():
                    raise IntegrityError("Idempotency key reused. Prevented duplicate transaction.")

                # Fraud Detection / Rate Limiting Logic: 
                # Count transactions in the past 60 seconds
                sixty_seconds_ago = timezone.now() - timezone.timedelta(seconds=60)
                recent_txs = WalletTransaction.objects.filter(
                    wallet=wallet, 
                    timestamp__gte=sixty_seconds_ago
                ).count()
                
                if recent_txs > 5:
                    wallet.status = 'FROZEN'
                    wallet.save()
                    raise SecurityAlert("Fraud detected: High-frequency transactions. Wallet Frozen.")

                # Calculate New Balance & Validate
                if tx_type == 'CREDIT':
                    new_balance = wallet.balance + amount
                else:
                    new_balance = wallet.balance - amount
                    if new_balance < 0:
                        raise ValidationError("Insufficient funds for debit transaction.")

                # Create Append-Only Ledger Entry
                ledger_entry = WalletTransaction(
                    wallet=wallet,
                    tx_type=tx_type,
                    amount=amount,
                    running_balance=new_balance,
                    category=category,
                    idempotency_key=idempotency_key,
                    metadata=metadata or {}
                )
                
                # Cryptographic Security Signature (HMAC simulation via SHA-256)
                # Ensure it's generated BEFORE save using pre-calculated state properties.
                ledger_entry.security_hash = ledger_entry.calculate_integrity_hash()
                ledger_entry.save()

                # Commit New Balance
                wallet.balance = new_balance
                wallet.save()

                # Audit Trail Verification Logic: Strict Check
                if (wallet.balance != ledger_entry.running_balance):
                    # Trigger automatic database rollback
                    raise ValidationError("Atomic Rollback: Ledger state-balance mismatch. Fatal Error.")

                return ledger_entry
                
        except Wallet.DoesNotExist:
            raise ValidationError("Critical Error: Wallet does not exist for this user.")
