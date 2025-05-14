import requests
import json

# Set API keys directly
API_KEY = "c997e201e99cf5899683"
SECRET_KEY = "cd6e6eb6fec9d07601589ce2837bda1afa6c306d368c0e3ed98a72a155c692a6"

# Create a test file
with open("test_file.json", "w") as f:
    json.dump({"test": "data"}, f)

# Prepare for upload
url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
headers = {
    'pinata_api_key': API_KEY,
    'pinata_secret_api_key': SECRET_KEY
}

# Prepare metadata
payload = {
    'pinataMetadata': json.dumps({
        'name': 'test_file.json',
        'keyvalues': {
            'source': 'test_script'
        }
    })
}

# Open and upload file
with open("test_file.json", "rb") as file_data:
    files = {
        'file': ('test_file.json', file_data)
    }
    
    # Make the request
    print(f"Making request to Pinata with API Key: {API_KEY[:5]}...")
    response = requests.post(
        url,
        headers=headers,
        files=files,
        data=payload
    )
    
    # Print results
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text}")