"""
Detection Service using Hugging Face Inference API
This version calls Hugging Face API instead of loading model locally
Perfect for deployment on Render free tier!
"""
import requests
import os
from PIL import Image
import io
import base64

# Hugging Face API configuration
HF_API_URL = "https://api-inference.huggingface.co/models/IDEA-Research/grounding-dino-base"
HF_API_TOKEN = os.environ.get('HUGGINGFACE_API_TOKEN', '')  # Set this in Render environment variables

# Detection configuration
DETECTION_THRESHOLD = 0.3
TEXT_PROMPT = (
    "cow head. cow nose. cow eye. cow ear. "
    "cow neck. cow body. cow leg. cow hoof. "
    "cow udder. cow tail."
)


def detect_body_parts_hf_api(image_path: str):
    """
    Detect cattle body parts using Hugging Face Inference API
    
    Args:
        image_path: Path to image file
        
    Returns:
        tuple: (detections, body_parts)
            - detections: List of detection dicts with label, confidence, bbox
            - body_parts: Dict mapping body part names to bounding boxes
    """
    print(f"[HF API] Detecting body parts in: {image_path}")
    
    # Read and encode image
    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    
    # Prepare request
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}"
    }
    
    # Hugging Face API payload
    payload = {
        "inputs": {
            "image": base64.b64encode(image_bytes).decode('utf-8'),
            "text": TEXT_PROMPT
        },
        "parameters": {
            "threshold": DETECTION_THRESHOLD
        }
    }
    
    print(f"[HF API] Sending request to Hugging Face...")
    
    try:
        # Call Hugging Face API
        response = requests.post(
            HF_API_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            print(f"[HF API] ✓ Received response from Hugging Face")
            
            # Parse results
            detections, body_parts = parse_hf_results(results, image_path)
            
            print(f"[HF API] ✓ Detected {len(detections)} body parts")
            print(f"[HF API] ✓ Grouped into {len(body_parts)} regions")
            
            return detections, body_parts
            
        elif response.status_code == 503:
            # Model is loading
            print(f"[HF API] ⏳ Model is loading, please wait...")
            raise Exception("Model is loading on Hugging Face. Please try again in 20 seconds.")
            
        else:
            print(f"[HF API] ✗ Error: {response.status_code}")
            print(f"[HF API] Response: {response.text}")
            raise Exception(f"Hugging Face API error: {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"[HF API] ✗ Request timeout")
        raise Exception("Hugging Face API timeout. Please try again.")
        
    except Exception as e:
        print(f"[HF API] ✗ Error: {str(e)}")
        raise


def parse_hf_results(results, image_path):
    """
    Parse Hugging Face API results into our format
    
    Args:
        results: API response
        image_path: Path to image (for dimensions)
        
    Returns:
        tuple: (detections, body_parts)
    """
    # Get image dimensions
    image = Image.open(image_path)
    img_width, img_height = image.size
    
    detections = []
    body_part_groups = {}
    
    # Parse each detection
    for detection in results:
        label = detection.get('label', '').lower()
        score = detection.get('score', 0)
        box = detection.get('box', {})
        
        if score < DETECTION_THRESHOLD:
            continue
        
        # Convert normalized coordinates to pixel coordinates
        x1 = int(box.get('xmin', 0))
        y1 = int(box.get('ymin', 0))
        x2 = int(box.get('xmax', 0))
        y2 = int(box.get('ymax', 0))
        
        # Create detection dict
        det = {
            'label': label,
            'confidence': float(score),
            'bbox': [x1, y1, x2, y2]
        }
        detections.append(det)
        
        # Group by body part
        part_name = normalize_body_part_name(label)
        if part_name not in body_part_groups:
            body_part_groups[part_name] = []
        body_part_groups[part_name].append([x1, y1, x2, y2])
    
    # Merge overlapping detections
    body_parts = {}
    for part_name, bboxes in body_part_groups.items():
        if len(bboxes) == 1:
            body_parts[part_name] = bboxes[0]
        else:
            # Merge multiple detections of same part
            body_parts[part_name] = merge_bboxes(bboxes)
    
    return detections, body_parts


def normalize_body_part_name(label: str) -> str:
    """
    Normalize body part labels
    
    Args:
        label: Raw label from detection
        
    Returns:
        Normalized part name
    """
    label = label.lower().replace('cow ', '').strip()
    
    # Map similar parts
    if 'leg' in label or 'hoof' in label:
        # Number legs
        import re
        existing_legs = [k for k in body_part_groups.keys() if 'leg' in k]
        leg_num = len(existing_legs) + 1
        return f'leg_{leg_num}'
    
    return label


def merge_bboxes(bboxes):
    """
    Merge multiple bounding boxes into one
    
    Args:
        bboxes: List of [x1, y1, x2, y2]
        
    Returns:
        Merged bbox [x1, y1, x2, y2]
    """
    x1 = min(bbox[0] for bbox in bboxes)
    y1 = min(bbox[1] for bbox in bboxes)
    x2 = max(bbox[2] for bbox in bboxes)
    y2 = max(bbox[3] for bbox in bboxes)
    
    return [x1, y1, x2, y2]


# Fallback to local model if API fails
def detect_body_parts(image_path: str):
    """
    Main detection function with fallback
    Tries HF API first, falls back to local model if needed
    """
    try:
        # Try Hugging Face API first
        return detect_body_parts_hf_api(image_path)
    except Exception as e:
        print(f"[Detection] HF API failed: {str(e)}")
        print(f"[Detection] Falling back to local model...")
        
        # Import local detection as fallback
        try:
            from .detection_service import detect_body_parts as local_detect
            return local_detect(image_path)
        except Exception as e2:
            print(f"[Detection] Local model also failed: {str(e2)}")
            raise Exception(f"Both HF API and local model failed. HF: {str(e)}, Local: {str(e2)}")
