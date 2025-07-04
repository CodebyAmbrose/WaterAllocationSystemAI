import requests

print("Resetting analytics to zero...")
response = requests.post('http://localhost:8000/analytics/reset')
print(f"Status: {response.status_code}")
print(f"Response: {response.json()}") 