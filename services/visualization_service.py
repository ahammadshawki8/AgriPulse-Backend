"""
Visualization Service
Generate annotated images with body part detections
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
import config


def draw_detections(image_path, detections, body_parts, output_path=None):
    """
    Draw detections on image
    
    Args:
        image_path: Path to original image
        detections: List of detection dicts
        body_parts: Dict of grouped body parts
        output_path: Where to save (optional)
        
    Returns:
        Path to saved annotated image
    """
    # Load image
    img = cv2.imread(str(image_path))
    
    # Colors for different parts
    colors = {
        'head': (0, 255, 0),      # Green
        'nose': (0, 255, 255),    # Yellow
        'eye': (255, 255, 0),     # Cyan
        'ear': (0, 255, 0),       # Green
        'leg': (255, 0, 255),     # Magenta
        'hoof': (255, 0, 255),    # Magenta
        'udder': (0, 165, 255),   # Orange
        'tail': (128, 0, 128),    # Purple
        'neck': (0, 128, 255),    # Light blue
        'body': (128, 128, 128)   # Gray
    }
    
    # Draw all individual detections (thin lines)
    for det in detections:
        label = det['label']
        confidence = det['confidence']
        bbox = det['bbox']
        
        x1, y1, x2, y2 = map(int, bbox)
        
        # Choose color
        color = (0, 255, 0)  # default green
        for key, col in colors.items():
            if key in label.lower():
                color = col
                break
        
        # Draw thin box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 1)
        
        # Draw label
        text = f"{label}: {confidence:.2f}"
        font_scale = 0.4
        thickness = 1
        
        (text_w, text_h), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )
        
        # Background for text
        cv2.rectangle(
            img,
            (x1, y1 - text_h - 4),
            (x1 + text_w + 4, y1),
            color,
            -1
        )
        
        # Text
        cv2.putText(
            img, text, (x1 + 2, y1 - 2),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), thickness
        )
    
    # Draw grouped body parts (thick lines)
    for part_name, bbox in body_parts.items():
        x1, y1, x2, y2 = bbox
        
        # Choose color
        color = (255, 255, 255)  # default white
        for key, col in colors.items():
            if key in part_name.lower():
                color = col
                break
        
        # Draw thick box
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 3)
        
        # Draw part name
        text = part_name.upper()
        font_scale = 0.7
        thickness = 2
        
        (text_w, text_h), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )
        
        # Background for text
        cv2.rectangle(
            img,
            (x1, y2 + 5),
            (x1 + text_w + 10, y2 + text_h + 15),
            color,
            -1
        )
        
        # Text
        cv2.putText(
            img, text, (x1 + 5, y2 + text_h + 10),
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 0), thickness
        )
    
    # Save
    if output_path is None:
        # Generate output path
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = config.RESULT_FOLDER / f"annotated_{timestamp}.jpg"
    
    cv2.imwrite(str(output_path), img)
    
    return output_path


def create_detection_summary_image(image_path, detections, body_parts):
    """
    Create a summary image with detection info
    
    Args:
        image_path: Path to original image
        detections: List of detections
        body_parts: Dict of body parts
        
    Returns:
        Path to summary image
    """
    # Load image
    img = cv2.imread(str(image_path))
    h, w = img.shape[:2]
    
    # Create summary panel
    panel_width = 400
    panel = np.ones((h, panel_width, 3), dtype=np.uint8) * 255
    
    # Add title
    cv2.putText(
        panel, "Detection Summary", (10, 30),
        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2
    )
    
    # Add body parts count
    y_pos = 70
    cv2.putText(
        panel, f"Body Parts: {len(body_parts)}", (10, y_pos),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1
    )
    
    # List body parts
    y_pos += 30
    for part_name in body_parts.keys():
        cv2.putText(
            panel, f"- {part_name}", (20, y_pos),
            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1
        )
        y_pos += 25
        if y_pos > h - 50:
            break
    
    # Add detections count
    y_pos += 20
    cv2.putText(
        panel, f"Total Detections: {len(detections)}", (10, y_pos),
        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1
    )
    
    # Combine image and panel
    combined = np.hstack([img, panel])
    
    # Save
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = config.RESULT_FOLDER / f"summary_{timestamp}.jpg"
    
    cv2.imwrite(str(output_path), combined)
    
    return output_path
