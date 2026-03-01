"""
Test Hugging Face Inference API
Quick script to verify your HF token works
"""
import requests
import os
from pathlib import Path

# Get token from environment or .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

HF_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN', '')

if not HF_TOKEN:
    print("❌ Error: HUGGINGFACE_API_TOKEN not found!")
    print("Please set it in .env file or environment variable")
    exit(1)

print(f"✓ Token found: {HF_TOKEN[:10]}...")

# Test image path - try multiple locations
possible_paths = [
    Path("input/cow1.jpg"),
    Path("../input/cow1.jpg"),
    Path("uploads/cow1.jpg")
]

image_path = None
for path in possible_paths:
    if path.exists():
        image_path = path
        break

if not image_path:
    print(f"❌ Error: Image not found!")
    print(f"Tried: {[str(p) for p in possible_paths]}")
    exit(1)

print(f"✓ Image found: {image_path}")

# Prepare request (UPDATED ENDPOINT)
url = "https://router.huggingface.co/models/IDEA-Research/grounding-dino-base"
headers = {"Authorization": f"Bearer {HF_TOKEN}"}

print(f"\n🚀 Testing Hugging Face API...")
print(f"URL: {url}")

# Read image
with open(image_path, 'rb') as f:
    image_data = f.read()

print(f"Image size: {len(image_data)} bytes")

# Make request
try:
    response = requests.post(
        url,
        headers=headers,
        files={"file": image_data},
        timeout=30
    )
    
    print(f"\n📊 Response:")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ SUCCESS! API is working!")
        result = response.json()
        print(f"\nDetections: {len(result) if isinstance(result, list) else 'N/A'}")
        if isinstance(result, list) and len(result) > 0:
            print("\nFirst few detections:")
            for i, det in enumerate(result[:3]):
                print(f"  {i+1}. {det}")
    
    elif response.status_code == 503:
        print("⏳ Model is loading... Please wait 20 seconds and try again")
        print("This is normal for the first request!")
    
    elif response.status_code == 401:
        print("❌ Unauthorized! Check your HF token")
        print("Make sure it's a valid token with Read permission")
    
    else:
        print(f"❌ Error: {response.status_code}")
        print(f"Response: {response.text}")

except requests.exceptions.Timeout:
    print("❌ Request timeout! API took too long to respond")
    
except Exception as e:
    print(f"❌ Error: {str(e)}")

print("\n" + "="*50)
