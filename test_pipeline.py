import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.scraper.normalization import CleanDataService, UnifiedSchemaMapper
from apps.scraper.matcher import ProductSimilarityEngine, match_products_across_stores
from apps.dashboard.services import MatrixConstructor
from apps.dashboard.intelligence import MatrixIntelligenceEngine

def run_pipeline_test():
    print("--- Testing Normalization ---")
    val1 = CleanDataService.to_decimal("₹ 1,500.50")
    val2 = CleanDataService.to_decimal("$20.00")
    print(f" INR 1,500.50 -> {val1}")
    print(f" $20.00 -> {val2}")

    print("\n--- Testing Similarity Engine ---")
    title_a = "Apple iPhone 15 Pro Max (Black Titanium)"
    title_b = "iPhone 15 Pro Max Black Titanium 256GB"
    score = ProductSimilarityEngine.get_similarity_score(title_a, title_b)
    print(f"Comparing: '{title_a}' vs '{title_b}'")
    print(f"Fuzzy Match Score: {score:.2f}")

    print("\n--- Testing Full Matrix Pipeline ---")
    raw_amazon = {'title': 'Sony WH-1000XM5 Wireless Headphones', 'price': 'INR 29,990', 'url': 'http://amazon.in/sony'}
    raw_flipkart = {'title': 'Sony WH 1000XM5 Bluetooth Headset', 'price': 'INR 26,990', 'url': 'http://flipkart.com/sony'}
    
    p1 = UnifiedSchemaMapper.map_store_data(raw_amazon, 'Amazon')
    p2 = UnifiedSchemaMapper.map_store_data(raw_flipkart, 'Flipkart')
    
    product_list = [
        {'title': p1.title, 'price': p1.price, 'store': p1.store_name, 'url': p1.url},
        {'title': p2.title, 'price': p2.price, 'store': p2.store_name, 'url': p2.url}
    ]
    
    grouped = match_products_across_stores(product_list)
    matrix_rows = MatrixConstructor.build_intelligence_matrix(grouped)
    final_output = MatrixIntelligenceEngine.inject_matrix_intelligence(matrix_rows)
    
    import json
    print(json.dumps(final_output, indent=2, default=str))

if __name__ == "__main__":
    run_pipeline_test()
