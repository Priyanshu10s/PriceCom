from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from typing import Dict, Any, List
from apps.scraper.models import NotificationLog
from collections import Counter

class AlertMetricsManager:
    """
    The Metric Reporting Engine.
    Transforms raw audit data into high-level professional metrics.
    """
    
    @staticmethod
    def generate_30_day_report() -> Dict[str, Any]:
        """
        Generates a Mentor-Ready 30-day performance report.
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        # Aggregation Query
        stats = NotificationLog.objects.filter(
            intent_timestamp__range=(start_date, end_date)
        ).aggregate(
            total=Count('id'),
            sent=Count('id', filter=Q(status='SENT')),
            failed=Count('id', filter=Q(status='FAILED')),
            suppressed=Count('id', filter=Q(status='SUPPRESSED')) # If we had suppressed logs
        )
        
        total = stats['total'] or 0
        sent = stats['sent'] or 0
        
        success_rate = (sent / total * 100) if total > 0 else 0.0
        
        return {
            "period": "Last 30 Days",
            "total_alerts": total,
            "successful_deliveries": sent,
            "failed_deliveries": stats['failed'] or 0,
            "suppressed_alerts": stats['suppressed'] or 0,
            "success_rate": round(success_rate, 2)
        }

def get_failed_analysis() -> List[tuple]:
    """
    The 'Instant Debugger' Utility.
    Aggregates common SMTP errors for Root Cause Analysis.
    """
    # Get all error messages from failed logs
    errors = NotificationLog.objects.filter(status='FAILED').values_list('error_message', flat=True)
    
    # Group by first 50 chars to identify patterns
    # e.g. "SMTPAuthenticationError: ..."
    error_patterns = [e[:50] for e in errors if e]
    
    return Counter(error_patterns).most_common(5)

class MarketStabilityEngine:
    """
    High-Precision Market Stability Engine.
    Calculates Volatility Score and Market Stability Index.
    """
    
    @staticmethod
    def calculate_market_risk(price_history_records: List[Any]) -> Dict[str, Any]:
        """
        The sigma Engine. Calculates Standard Deviation and Mean Price.
        Implements Coefficient of Variation (CV).
        """
        from decimal import Decimal
        import numpy as np
        
        history = list(price_history_records)
        if len(history) < 5:
            return {
                "status": "INITIALIZING",
                "volatility_score": 0.0,
                "high_volatility": False,
                "advice": "Gathering data"
            }
            
        prices = []
        for h in history:
            # Handle both ORM objects and dictionaries
            val = h.price if hasattr(h, 'price') else h['price']
            prices.append(float(val))
            
        # Select last 30 points
        prices = prices[:30]
        
        std_dev = np.std(prices)
        mean_price = np.mean(prices)
        
        cv = (std_dev / mean_price) * 100 if mean_price > 0 else 0.0
        
        # Stability Mapping
        if cv < 2.0:
            status = "STABLE"
            high_volatility = False
        elif cv < 7.0:
            status = "MODERATE"
            high_volatility = False
        else:
            status = "HIGHLY_VOLATILE"
            high_volatility = True
            
        # Moving Average Convergence (SMA vs EMA)
        # Using 7-day and 21-day approximations based on data points
        sma_7 = np.mean(prices[:7]) if len(prices) >= 7 else mean_price
        
        # Simple EMA calculation
        def calculate_ema(data, period):
            if len(data) < period:
                return np.mean(data)
            alpha = 2.0 / (period + 1.0)
            ema = data[-1]
            for price in reversed(data[:-1]):
                ema = (price * alpha) + (ema * (1 - alpha))
            return ema
            
        ema_7 = calculate_ema(prices, 7)
        ema_21 = calculate_ema(prices, 21)
        
        # Volatility Warning
        warning_triggered = ema_7 < sma_7 and high_volatility
        
        advice = MarketStabilityEngine.get_volatility_advice(status, warning_triggered)
        
        return {
            "status": status,
            "cv_percentage": round(cv, 2),
            "volatility_score": round(std_dev, 2),
            "high_volatility": high_volatility,
            "advice": advice,
            "ema_7": round(ema_7, 2),
            "sma_7": round(sma_7, 2)
        }

    @staticmethod
    def get_volatility_advice(status: str, warning_triggered: bool) -> str:
        if status == "HIGHLY_VOLATILE":
            if warning_triggered:
                return "Price is fluctuating rapidly. Expect a drop soon, but wait for the dip."
            return "Market is highly volatile. Proceed with caution."
        elif status == "MODERATE":
            return "Normal market fluctuations observed."
        return "Price is stable."

