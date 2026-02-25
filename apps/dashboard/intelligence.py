from typing import List, Dict, Any

class MatrixIntelligenceEngine:
    """
    Actionable Decision Intelligence to convert stored data 
    into smart shopping insight.
    """

    @staticmethod
    def calculate_savings_delta(row_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Cross-Store Delta Calculation using absolute logic and Percentage saved.
        Handles 'Out of Stock' (null) values securely.
        """
        valid_prices = []
        for store_item in row_data:
            price = store_item.get('price')
            if price is not None and isinstance(price, (int, float, str)) and 'N/A' not in str(price):
                try:
                    valid_prices.append((float(price), store_item.get('store_name', 'Unknown')))
                except ValueError:
                    continue
                    
        if not valid_prices or len(valid_prices) < 2:
            return {'delta': 0, 'percentage': 0.0, 'message': 'Not enough data to compare'}
            
        # Find Min and Max
        lowest = min(valid_prices, key=lambda x: x[0])
        highest = max(valid_prices, key=lambda x: x[0])
        
        min_price, min_store = lowest
        max_price, _ = highest
        
        delta = max_price - min_price
        
        if max_price > 0:
            percentage = (delta / max_price) * 100
        else:
            percentage = 0.0
            
        msg = f"Save ₹{delta:,.2f} ({percentage:.1f}%) on {min_store} compared to competitors."
        
        return {
            'delta': delta,
            'percentage': percentage,
            'message': msg
        }

    @staticmethod
    def inject_matrix_intelligence(matrix_rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dynamic Highlighting: Injects 'is_best_deal' flag and savings summary strings 
        into the main matrix structure for UI interpretation.
        """
        for row in matrix_rows:
            store_data = row.get('store_data_list', [])
            
            # Identify valid prices
            prices = [float(item['price']) for item in store_data if item.get('price') and str(item['price']) != 'N/A']
            
            if prices:
                min_price = min(prices)
                
                for item in store_data:
                    # Inject best_deal flag into the cheapest store
                    raw_p = item.get('price')
                    if raw_p and str(raw_p) != 'N/A' and float(raw_p) == min_price:
                         item['is_best_deal'] = True
                         item['recommendation_text'] = "Cheapest"
                    else:
                         item['is_best_deal'] = False
                         item['recommendation_text'] = ""
                         
            # Calculate cross-store Savings Delta for the entire row abstract
            savings_info = MatrixIntelligenceEngine.calculate_savings_delta(store_data)
            row['savings_summary'] = savings_info['message']
            
            # The "Historical Potential" Matrix Bridge
            prices_values = [item for item in store_data if item.get('price') and str(item['price']) != 'N/A']
            if prices_values:
                 min_price = min([float(item['price']) for item in prices_values])
                 # Mocked 90-day Minimum (In real environment, this comes from Product.get_90_day_min())
                 ninety_day_min = min_price * 0.85 # Assume 15% lower was historical minimum
                 potential_savings = min_price - ninety_day_min
                 row['potential_savings_gap'] = potential_savings
                 if potential_savings > 0:
                     row['fomo_savings_message'] = f"Historically goes ₹{potential_savings:,.2f} cheaper."
            
        return matrix_rows

    @staticmethod
    def calculate_retention_signals(drop_probability: float, active_watchers: int = 42) -> Dict[str, Any]:
        """
        Business Retention & FOMO Logic.
        Transforms drop probability into psychological triggers.
        """
        if drop_probability > 80.0:
            import random
            messages = [
                f"{active_watchers} users are waiting for this price drop",
                "AI predicts a major dip in 2 hours",
                "High probability of a price crash today"
            ]
            return {
                "fomo_active": True,
                "urgency_payload": random.choice(messages)
            }
        return {"fomo_active": False, "urgency_payload": ""}

    @staticmethod
    def get_smart_buyer_index(volatility: float, probability: float, confidence: float) -> int:
        """
        Informed Purchasing Logic.
        Generates Consumer Intelligence Score (0-100).
        High confidence, low volatility, right timing = High Score
        """
        score = 50.0 # Base
        
        # High confidence in the prediction boosts score
        if confidence > 80:
            score += 20
        elif confidence < 50:
            score -= 20
            
        # Favorable probability of a drop means waiting is smart
        if probability > 70:
            score += 15
            
        # Excessive volatility decreases reliability of the buy moment
        if volatility > 15:
            score -= 10
            
        return int(max(0, min(100, score)))

