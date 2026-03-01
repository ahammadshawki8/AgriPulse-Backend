"""
Detection Service using HuggingFace Space API
Calls your custom HuggingFace Space that hosts Grounding DINO
Uses Gradio Client for reliable API calls
"""
import os
import base64
import json

try:
    from gradio_client import Client
except ImportError:
    print("[HF Space] Installing gradio_client...")
    import subprocess
    subprocess.check_call(["pip", "install", "-q", "gradio_client"])
    from gradio_client import Client

# HuggingFace Space configuration
SPACE_USERNAME = os.environ.get('HF_SPACE_USERNAME', 'YOUR_USERNAME')
SPACE_NAME = os.environ.get('HF_SPACE_NAME', 'cattle-detection-api')
SPACE_URL = f"https://{SPACE_USERNAME}-{SPACE_NAME}.hf.space"

# Detection configuration
DETECTION_THRESHOLD = 0.3

# Cache the client
_client = None

def get_client():
    """Get or create Gradio client (singleton)"""
    global _client
    if _client is None:
        print(f"[HF Space] Connecting to Space: {SPACE_URL}")
        _client = Client(SPACE_URL)
        print(f"[HF Space] ✓ Connected to Space")
    return _client


def detect_body_parts_hf_space(image_path: str):
    """
    Detect cattle body parts using HuggingFace Space API
    
    Args:
        image_path: Path to image file
        
    Returns:
        tuple: (detections, body_parts)
            - detections: List of detection dicts with label, confidence, bbox
            - body_parts: Dict mapping body part names to bounding boxes
    """
    print(f"[HF Space] Detecting body parts in: {image_path}")
    
    try:
        # Read and encode image as base64
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        print(f"[HF Space] Image size: {len(image_bytes)} bytes")
        print(f"[HF Space] Calling Space API...")
        
        # Get client
        client = get_client()
        
        # Call Space API using Gradio Client
        result = client.predict(
            image_base64,           # Base64 encoded image
            DETECTION_THRESHOLD,    # Threshold
            api_name="/lambda_1"    # Base64 endpoint
        )
        
        print(f"[HF Space] ✓ Received response from Space")
        
        # Parse result
        if isinstance(result, str):
            result = json.loads(result)
        
        if result.get("success"):
            detections = result.get("detections", [])
            body_parts = result.get("body_parts", {})
            
            print(f"[HF Space] ✓ Detected {len(detections)} body parts")
            print(f"[HF Space] ✓ Grouped into {len(body_parts)} regions")
            
            return detections, body_parts
        else:
            error = result.get("error", "Unknown error")
            print(f"[HF Space] ✗ Detection failed: {error}")
            raise Exception(f"Detection failed: {error}")
            
    except Exception as e:
        print(f"[HF Space] ✗ Error: {str(e)}")
        raise


def detect_body_parts(image_path: str):
    """
    Main detection function with fallback
    Tries HF Space first, falls back to local model if needed
    """
    try:
        # Try HuggingFace Space first
        return detect_body_parts_hf_space(image_path)
    except Exception as e:
        print(f"[Detection] HF Space failed: {str(e)}")
        print(f"[Detection] Falling back to local model...")
        
        # Import local detection as fallback
        try:
            from .detection_service import detect_body_parts as local_detect
            return local_detect(image_path)
        except Exception as e2:
            print(f"[Detection] Local model also failed: {str(e2)}")
            raise Exception(f"Both HF Space and local model failed. Space: {str(e)}, Local: {str(e2)}")


# Test function
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python detection_service_hf_space.py <image_path>")
        sys.exit(1)
    
    image_path = sys.argv[1]
    
    print(f"\n{'='*60}")
    print("Testing HuggingFace Space Detection")
    print(f"{'='*60}\n")
    
    try:
        detections, body_parts = detect_body_parts_hf_space(image_path)
        
        print(f"\n✅ Success!")
        print(f"\nDetections ({len(detections)}):")
        for det in detections[:5]:
            print(f"  - {det['label']}: {det['confidence']:.2f}")
        
        print(f"\nBody Parts ({len(body_parts)}):")
        for part, bbox in list(body_parts.items())[:5]:
            print(f"  - {part}: {bbox}")
            
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
