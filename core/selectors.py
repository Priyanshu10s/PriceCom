class StoreSelector:
    AMAZON = {
        "title": "#productTitle",
        "price": ".a-price .a-offscreen",  # Amazon often has multiple price elements, this is a common one
        "image": "#landingImage",
    }
    
    FLIPKART = {
        "title": ".B_NuCI",
        "price": "._30jeq3._16Jk6d",
        "image": "._396cs4._2amPTt._3qGmMb",
    }
