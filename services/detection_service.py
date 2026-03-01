"""
Detection Service - Grounding DINO Integration
Handles body part detection for cattle health monitoring
"""
import torch
from PIL import Image
from pathlib import Path
from transformers import AutoProcessor, AutoModelForZeroShotObjectDetection
import config


class GroundingDINODetector:
    """Singleton Grounding DINO detector - loads model once"""
    
    _instance = None
    _model = None
    _processor = None
    _device = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GroundingDINODetector, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize model (called once)"""
        if self._model is None:
            print(f"Loading Grounding DINO: {config.GROUNDING_DINO_MODEL}")
            
            self._device = "cuda" if torch.cuda.is_available() else "cpu"
            print(f"Using device: {self._device}")
            
            self._processor = AutoProcessor.from_pretrained(config.GROUNDING_DINO_MODEL)
            self._model = AutoModelForZeroShotObjectDetection.from_pretrained(
                config.GROUNDING_DINO_MODEL
            )
            self._model.to(self._device)
            
            print("✓ Grounding DINO loaded successfully!")
    
    def detect(self, image_path, threshold=None):
        """
        Detect body parts in image
        
        Args:
            image_path: Path to image file
            threshold: Detection confidence threshold (default from config)
            
        Returns:
            tuple: (detections, body_parts)
                - detections: List of all detections with labels, scores, boxes
                - body_parts: Grouped body parts dict {part_name: [x1, y1, x2, y2]}
        """
        if threshold is None:
            threshold = config.DETECTION_THRESHOLD
        
        # Load image
        image = Image.open(image_path)
        
        # Prepare inputs
        inputs = self._processor(
            images=image,
            text=config.TEXT_PROMPT,
            return_tensors="pt"
        ).to(self._device)
        
        # Run inference
        with torch.no_grad():
            outputs = self._model(**inputs)
        
        # Post-process results
        results = self._processor.post_process_grounded_object_detection(
            outputs,
            inputs.input_ids,
            threshold=threshold,
            target_sizes=[image.size[::-1]]
        )[0]
        
        # Format detections
        detections = []
        for score, label, box in zip(
            results["scores"],
            results["labels"],
            results["boxes"]
        ):
            detections.append({
                "label": label,
                "confidence": float(score),
                "bbox": box.cpu().numpy().tolist()
            })
        
        # Group into body parts
        body_parts = self._group_body_parts(detections)
        
        return detections, body_parts
    
    def _group_body_parts(self, detections):
        """
        Group detections into logical body part regions
        
        Args:
            detections: List of detection dicts
            
        Returns:
            dict: {part_name: [x1, y1, x2, y2]}
        """
        body_parts = {}
        
        for det in detections:
            label = det['label'].lower()
            box = [int(x) for x in det['bbox']]
            
            # Group head-related parts
            if any(keyword in label for keyword in ['head', 'nose', 'ear', 'eye']):
                if 'head' not in body_parts:
                    body_parts['head'] = box
                else:
                    # Merge boxes (take min/max to encompass all)
                    existing = body_parts['head']
                    body_parts['head'] = [
                        min(existing[0], box[0]),
                        min(existing[1], box[1]),
                        max(existing[2], box[2]),
                        max(existing[3], box[3])
                    ]
            
            # Udder
            elif 'udder' in label:
                body_parts['udder'] = box
            
            # Legs and hooves
            elif any(keyword in label for keyword in ['leg', 'hoof']):
                # Create separate entries for each leg
                leg_num = len([k for k in body_parts.keys() if 'leg' in k]) + 1
                body_parts[f'leg_{leg_num}'] = box
            
            # Tail
            elif 'tail' in label:
                body_parts['tail'] = box
            
            # Neck
            elif 'neck' in label:
                body_parts['neck'] = box
            
            # Body
            elif 'body' in label:
                body_parts['body'] = box
        
        return body_parts


# Global detector instance
_detector_instance = None


def get_detector():
    """Get or create detector instance"""
    global _detector_instance
    if _detector_instance is None:
        _detector_instance = GroundingDINODetector()
    return _detector_instance


def detect_body_parts(image_path, threshold=None):
    """
    Detect body parts in cattle image
    
    Args:
        image_path: Path to image file
        threshold: Detection confidence threshold
        
    Returns:
        tuple: (detections, body_parts)
    """
    detector = get_detector()
    return detector.detect(image_path, threshold)
