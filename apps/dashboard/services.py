from typing import List, Dict, Any

class MatrixConstructor:
    """
    Data Flattening Engine.
    Takes nested or heterogeneous inputs and strictly builds the 
    Actionable Intelligence Grid structure to prevent frontend errors.
    """

    @staticmethod
    def null_safety_handler(store_name: str) -> Dict[str, Any]:
        """
        The Availability Guard: 
        Ensures a structurally sound table row even if the Scraper failed or item is OOS.
        """
        return {
            'store': store_name,
            'price': 'N/A',
            'status': 'Notify Me',
            'is_available': False,
            'is_best_deal': False,
            'recommendation_text': ''
        }
        
    @staticmethod
    def build_intelligence_matrix(grouped_products: List[List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Matrix Flattening context constructor.
        Takes Semantic Matches and maps them to ['Amazon', 'Flipkart'] columns.
        """
        unified_matrix = []
        
        target_stores = ['Amazon', 'Flipkart']
        
        for group in grouped_products:
            # Determine the Primary Row Key
            primary_name = group[0].get('title', 'Unknown Value')
            
            store_parallel_data = []
            
            # Map known stores
            for store in target_stores:
                # Find product for this store
                store_item = next((item for item in group if store.lower() in str(item.get('store', '')).lower()), None)
                
                if store_item:
                    # Sanitize object for dashboard view
                    store_item['is_available'] = True
                    store_item['status'] = 'In Stock'
                    store_parallel_data.append(store_item)
                else:
                    # Implement safe null placeholders
                    store_parallel_data.append(MatrixConstructor.null_safety_handler(store))
                    
            unified_matrix.append({
                'common_product_name': primary_name,
                'store_data_list': store_parallel_data
            })
            
        return unified_matrix
