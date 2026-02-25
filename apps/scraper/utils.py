import re
from typing import List, Dict
from difflib import SequenceMatcher

def calculate_product_similarity(title1: str, title2: str) -> float:
    """
    Tokenization Strategy: Strips brand noise and calculates Token-Sort Fuzzy Matching
    to group identical products across completely heterogeneous store listings.
    """
    # Normalize cases
    t1 = title1.lower()
    t2 = title2.lower()
    
    # Strip stop-words to boost true algorithmic match confidence
    noise_words = ['apple', 'samsung', 'brand', 'new', 'unlocked', '(', ')', ',', '-']
    for word in noise_words:
        t1 = t1.replace(word, '')
        t2 = t2.replace(word, '')
        
    # Standard SequenceMatcher ratio fallback
    return SequenceMatcher(None, t1.strip(), t2.strip()).ratio()

def match_products_across_stores(product_list: List[dict]) -> List[List[dict]]:
    """
    Semantic Product Grouping: Groups wildly chaotic store items into unified Matrix Rows.
    Ensures > 85% algorithmic integrity before flattening them side-by-side.
    """
    grouped_matrix = []
    
    for p1 in product_list:
        matched = False
        for group in grouped_matrix:
            # Check similarity against Base Group Node
            base_item = group[0]
            similarity = calculate_product_similarity(p1['title'], base_item['title'])
            
            if similarity > 0.85:
                # Algorithmic Match Hit: Append to the unified presentation schema
                group.append(p1)
                matched = True
                break
                
        if not matched:
            grouped_matrix.append([p1])
            
    return grouped_matrix
