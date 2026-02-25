
import urllib.request
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context

url = 'https://bootstrap.pypa.io/get-pip.py'
output = 'get-pip.py'

print(f"Downloading {url}...")
try:
    with urllib.request.urlopen(url) as response, open(output, 'wb') as out_file:
        data = response.read()
        out_file.write(data)
    print("Download complete.")
except Exception as e:
    print(f"Error: {e}")
