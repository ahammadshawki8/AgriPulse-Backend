"""
Test script for image upload endpoint
"""
import requests
from pathlib import Path

# Test image upload
url = 'http://localhost:5000/api/analyze'
image_path = Path(__file__).parent.parent / 'input' / 'cow1.jpg'
files = {'image': open(image_path, 'rb')}
data = {'animal_id': 'COW001'}

print("Testing image upload...")
print(f"URL: {url}")
print(f"File: {image_path}")
print(f"Animal ID: COW001\n")

response = requests.post(url, files=files, data=data)

print(f"Status Code: {response.status_code}")
print(f"Response:\n{response.json()}")
