"""
Test using Gradio Client (recommended way)
"""
import json
import base64
from pathlib import Path

try:
    from gradio_client import Client
except ImportError:
    print("Installing gradio_client...")
    import subprocess
    subprocess.check_call(["pip", "install", "gradio_client"])
    from gradio_client import Client

SPACE_URL = "https://ahammadshawki8-cattle-detection-api.hf.space"

print("Testing with Gradio Client...")
print(f"Space URL: {SPACE_URL}\n")

# Find test image
image_path = Path("../input/cow1.jpg")
if not image_path.exists():
    image_path = Path("input/cow1.jpg")

print(f"Image: {image_path}")

try:
    # Create client
    print("\nConnecting to Space...")
    client = Client(SPACE_URL)
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
    
    print(f"Base64 length: {len(image_base64)}")
    
    # Call the base64 API
    print("\nCalling detection API...")
    print("⏳ This may take 20-30 seconds...")
    
    result = client.predict(
        image_base64,  # Base64 encoded image
        0.3,           # Threshold
        api_name="/lambda_1"  # Base64 endpoint
    )
    
    print(f"\n✅ Success!")
    print(f"Result type: {type(result)}")
    
    if isinstance(result, str):
        import json
        result = json.loads(result)
    
    print(json.dumps(result, indent=2))
    
    if result.get('success'):
        detections = result.get('detections', [])
        body_parts = result.get('body_parts', {})
        
        print(f"\n📊 Summary:")
        print(f"  Detections: {len(detections)}")
        print(f"  Body Parts: {len(body_parts)}")
        
        if detections:
            print(f"\n🔍 Detected parts:")
            for det in detections[:5]:
                print(f"    - {det['label']}: {det['confidence']:.2f}")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
