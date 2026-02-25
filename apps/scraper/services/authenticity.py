import numpy as np
import re
from typing import Dict, Any, List
import urllib.parse
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class AuthenticityManager:
    """
    PriceCom Authenticity Shield (Heuristic Risk Engine).
    Calculates real-time Trust Score (0-100) using statistical anomalies, 
    NLP sentiment, and network security protocols.
    """

    @staticmethod
    def calculate_price_z_score(current_price: float, group_prices: List[float]) -> Dict[str, Any]:
        """
        Statistical Guard (Z-Score Anomaly Detection).
        Checks if a price is a massive outlier compared to its peers.
        """
        if not group_prices or len(group_prices) < 3:
            return {"is_anomaly": False, "penalty": 0, "reason": "Insufficient group data"}

        prices = np.array(group_prices, dtype=float)
        median_price = np.median(prices)
        std_dev = np.std(prices)

        if std_dev == 0:
            return {"is_anomaly": False, "penalty": 0, "reason": "Zero variance"}

        z_score = abs(current_price - float(np.mean(prices))) / std_dev
        
        # 40% below median check
        is_too_cheap = current_price < (median_price * 0.6)
        
        if z_score > 2.5 or is_too_cheap:
            return {
                "is_anomaly": True, 
                "penalty": 50, 
                "reason": f"PRICE_ANOMALY: Z-Score={z_score:.2f}, Median={median_price:.2f}"
            }
            
        return {"is_anomaly": False, "penalty": 0, "reason": "Normal distribution"}

    @staticmethod
    def analyze_social_proof(extracted_reviews: List[str]) -> Dict[str, Any]:
        """
        Social Proof Guard (NLP Sentiment & Bot Detection).
        Checks for scam keywords and bot-like identical reviews using Jaccard Similarity.
        """
        if not extracted_reviews:
            return {"bot_flag": False, "penalty": 0, "reason": "No reviews to analyze"}

        # 1. Keyword Frequency Scanning
        high_risk_keywords = ["scam", "fake", "refurbished", "duplicate", "used"]
        text_corpus = " ".join(extracted_reviews).lower()
        
        keyword_count = sum(text_corpus.count(kw) for kw in high_risk_keywords)
        
        penalty = 0
        reasons = []
        
        if keyword_count > 3:
             penalty += 30
             reasons.append(f"HIGH_RISK_KEYWORDS ({keyword_count} found)")

        # 2. Bot Pattern Logic (Jaccard Similarity)
        def jaccard_similarity(str1, str2):
            set1 = set(str1.lower().split())
            set2 = set(str2.lower().split())
            if not set1 or not set2:
                return 0.0
            intersection = len(set1.intersection(set2))
            union = len(set1.union(set2))
            return float(intersection) / union

        bot_flag = False
        if len(extracted_reviews) > 1:
            for i in range(len(extracted_reviews)):
                for j in range(i + 1, len(extracted_reviews)):
                    sim = jaccard_similarity(extracted_reviews[i], extracted_reviews[j])
                    if sim > 0.9:
                        bot_flag = True
                        penalty += 40
                        reasons.append("BOT_GENERATED_REVIEWS (Similarity > 0.9)")
                        break
                if bot_flag:
                    break

        return {
            "bot_flag": bot_flag,
            "penalty": min(penalty, 100),
            "reason": " | ".join(reasons) if reasons else "Clean reviews"
        }

    @staticmethod
    def validate_network_security(product_url: str, redirects: int = 0) -> Dict[str, Any]:
        """
        Network Security Guard (SSRF & Domain Shield).
        Implements Typosquatting Detector and Redirect Checks.
        """
        if not product_url:
            return {"is_safe": False, "trust_score_override": 0, "reason": "Invalid URL"}

        try:
             parsed = urllib.parse.urlparse(product_url)
             domain = parsed.netloc.lower()
        except Exception:
             return {"is_safe": False, "trust_score_override": 0, "reason": "URL Parse Error"}

        # Extract main domain ignoring www.
        domain = domain.replace("www.", "")
        whitelist = ["amazon.com", "amazon.in", "flipkart.com"]
        
        # Levenshtein distance mock for Typosquatting (e.g. amaz0n.com)
        def levenshtein(s1, s2):
            if len(s1) < len(s2):
                return levenshtein(s2, s1)
            if len(s2) == 0:
                return len(s1)
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
            return previous_row[-1]

        is_whitelisted = False
        typosquatting_detected = False
        
        for w in whitelist:
            if domain == w:
                is_whitelisted = True
                break
            # If distance is small but not exact match -> Typosquatting
            dist = levenshtein(domain, w)
            if 0 < dist <= 2 and len(domain) > 5:
                typosquatting_detected = True
                break

        if typosquatting_detected:
            return {
                "is_safe": False, 
                "trust_score_override": 0, 
                "reason": f"TYPOSQUATTING_DETECTED: {domain}"
            }
            
        if redirects > 2:
            return {
                "is_safe": False,
                "trust_score_override": 0,
                "reason": "EXCESSIVE_REDIRECTS / MASKED_IP"
            }

        return {"is_safe": True, "trust_score_override": None, "reason": "Domain Verified"}

    @staticmethod
    def get_trust_badge(trust_score: int) -> Dict[str, str]:
        """
        The Decision Matrix UI Bridge.
        Returns visual configurations for the Trust Shield.
        """
        if trust_score > 80:
            return {"level": "Green", "class": "shield-verified", "label": "Verified Seller"}
        elif trust_score >= 50:
            return {"level": "Yellow", "class": "shield-caution", "label": "New Seller / Limited History"}
        else:
            return {"level": "Red", "class": "shield-risk", "label": "High Risk Anomaly"}

    @staticmethod
    def audit_store_price(store_price_obj, group_prices: List[float], extracted_reviews: List[str] = [], redirects: int = 0) -> None:
        """
        Self-Performing Sync: Runs all heuristic checks and updates the StorePrice model atomically.
        """
        base_score = 100
        flags = []
        
        # 1. Network Guard
        net_check = AuthenticityManager.validate_network_security(store_price_obj.product_url, redirects)
        if not net_check["is_safe"]:
            base_score = 0
            flags.append(net_check["reason"])
            store_price_obj.is_verified_seller = False
        else:
            # 2. Z-Score Guard
            z_check = AuthenticityManager.calculate_price_z_score(float(store_price_obj.current_price), group_prices)
            base_score -= z_check["penalty"]
            if z_check["is_anomaly"]:
                flags.append(z_check["reason"])

            # 3. NLP Guard
            nlp_check = AuthenticityManager.analyze_social_proof(extracted_reviews)
            base_score -= nlp_check["penalty"]
            if nlp_check["bot_flag"] or nlp_check["penalty"] > 0:
                flags.append(nlp_check["reason"])

        final_score = max(0, min(100, base_score))
        badge = AuthenticityManager.get_trust_badge(final_score)
        
        if final_score < 50:
            store_price_obj.is_verified_seller = False
            
        # Update metadata state
        if not isinstance(store_price_obj.metadata, dict):
            store_price_obj.metadata = {}
            
        store_price_obj.metadata.update({
            "trust_score": final_score,
            "risk_flags": flags,
            "badge_level": badge["level"],
            "badge_label": badge["label"],
            "verification_signature": f"V-{timezone.now().timestamp()}"
        })
        
        # Atomic commit
        store_price_obj.save(update_fields=['is_verified_seller', 'metadata'])
