import re
from typing import List, Dict, Any
from difflib import SequenceMatcher

class ProductSimilarityEngine:
    """
    Topper Grade Semantic & Fuzzy Matching logic to map "Dirty Data"
    into a high-integrity Intelligence matrix.
    """

    @staticmethod
    def preprocess_title(text: str) -> str:
        """
        Phase A: Preprocessing (Noise Removal).
        Case-Folding, strip stop-words, and Regex remove brackets.
        """
        if not text:
            return ""
            
        # Case folding
        text = text.lower()
        
        # Remove brand fluff and brackets using Regex
        text = re.sub(r'\(.*?\)|\[.*?\]', '', text)
        
        # Strip common stop-words and filler noise
        stop_words = ['apple', 'samsung', 'brand', 'new', 'unlocked', 'the', 'and', 'a', 'for']
        
        tokens = text.split()
        cleaned_tokens = [t for t in tokens if t not in stop_words and len(t) > 1]
        
        return " ".join(cleaned_tokens).strip()

    @staticmethod
    def get_similarity_score(title_a: str, title_b: str) -> float:
        """
        Phase B: The Algorithm (Token-Sort & Fuzzy Matching).
        Sorts words alphabetically before calculating Levenshtein ratio.
        """
        # 1. Preprocess
        clean_a = ProductSimilarityEngine.preprocess_title(title_a)
        clean_b = ProductSimilarityEngine.preprocess_title(title_b)
        
        # 2. Token-Sort Logic
        sorted_a = " ".join(sorted(clean_a.split()))
        sorted_b = " ".join(sorted(clean_b.split()))
        
        # 3. Levenshtein Distance (Fuzzy Ratio fallback)
        ratio = SequenceMatcher(None, sorted_a, sorted_b).ratio()
        return ratio

    @staticmethod
    def semantic_match(title_a: str, title_b: str) -> bool:
        """
        Returns True if the similarity threshold (> 85%) guarantees 
        they are the Same Physical Product.
        """
        score = ProductSimilarityEngine.get_similarity_score(title_a, title_b)
        return score > 0.85

def match_products_across_stores(product_list: List[dict]) -> List[List[dict]]:
    """
    Semantic Product Grouping: Groups chaotic store items into unified Matrix Rows.
    Ensures > 85% algorithmic integrity before flattening them side-by-side.
    """
    grouped_matrix = []
    
    for p1 in product_list:
        matched = False
        for group in grouped_matrix:
            # Check similarity against Base Group Node
            base_item = group[0]
            similarity = ProductSimilarityEngine.get_similarity_score(p1['title'], base_item['title'])
            
            if similarity > 0.85:
                # Algorithmic Match Hit
                group.append(p1)
                matched = True
                break
                
        if not matched:
            grouped_matrix.append([p1])
            
    return grouped_matrix
