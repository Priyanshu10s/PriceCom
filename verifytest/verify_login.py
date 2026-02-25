import urllib.request

try:
    url = 'http://127.0.0.1:8000/accounts/login/'
    print(f"Attempting to fetch {url}...")
    with urllib.request.urlopen(url) as response:
        html = response.read().decode('utf-8')
        print(f"Response Code: {response.getcode()}")
        
        if "<title>Enter the Void | PriceCom</title>" in html:
            print("SUCCESS: Login page title found.")
        else:
            print("WARNING: Login page title NOT found.")
            
except Exception as e:
    print(f"ERROR: {e}")
