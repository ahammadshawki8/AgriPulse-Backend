"""
FLIR thermal data parser
Handles dummy FLIR data from frontend until real FLIR camera is available
"""
import json
import numpy as np
from typing import Dict, Tuple, Optional


class FLIRDataParser:
    """Parse and validate FLIR thermal data"""
    
    def __init__(self):
        pass
    
    def parse_thermal_data(self, thermal_data_json: str) -> Optional[np.ndarray]:
        """
        Parse thermal data from JSON string
        
        Args:
            thermal_data_json: JSON string containing thermal array
            
        Returns:
            numpy array of temperatures (height x width)
            or None if parsing fails
        """
        try:
            data = json.loads(thermal_data_json)
            
            # Expected format: {"thermal_array": [[temp1, temp2, ...], ...]}
            if 'thermal_array' in data:
                thermal_array = np.array(data['thermal_array'], dtype=np.float32)
                print(f"✓ Parsed thermal data: shape {thermal_array.shape}")
                return thermal_array
            
            # Alternative format: flat array with dimensions
            elif 'temperatures' in data and 'width' in data and 'height' in data:
                temps = np.array(data['temperatures'], dtype=np.float32)
                height = data['height']
                width = data['width']
                thermal_array = temps.reshape((height, width))
                print(f"✓ Parsed thermal data: shape {thermal_array.shape}")
                return thermal_array
            
            else:
                print("✗ Invalid thermal data format")
                return None
                
        except json.JSONDecodeError as e:
            print(f"✗ JSON decode error: {e}")
            return None
        except Exception as e:
            print(f"✗ Error parsing thermal data: {e}")
            return None
    
    def validate_thermal_data(self, thermal_array: np.ndarray) -> bool:
        """
        Validate thermal data
        
        Args:
            thermal_array: numpy array of temperatures
            
        Returns:
            True if valid, False otherwise
        """
        if thermal_array is None:
            return False
        
        # Check dimensions
        if len(thermal_array.shape) != 2:
            print(f"✗ Invalid thermal array dimensions: {thermal_array.shape}")
            return False
        
        # Check temperature range (reasonable for cattle: 30-45°C)
        min_temp = np.min(thermal_array)
        max_temp = np.max(thermal_array)
        
        if min_temp < 20 or max_temp > 50:
            print(f"⚠ Warning: Temperature range unusual: {min_temp:.1f}°C - {max_temp:.1f}°C")
            # Don't fail, just warn
        
        print(f"✓ Thermal data valid: {thermal_array.shape}, range {min_temp:.1f}-{max_temp:.1f}°C")
        return True
    
    def simulate_thermal_data(self, image_shape: Tuple[int, int], 
                            body_parts: Dict[str, list]) -> np.ndarray:
        """
        Simulate thermal data for testing
        
        Args:
            image_shape: (height, width) of image
            body_parts: Dictionary of body parts with bounding boxes
            
        Returns:
            Simulated thermal array
        """
        h, w = image_shape[:2]
        
        # Base temperature (normal ambient)
        thermal_data = np.random.normal(37.5, 0.5, (h, w)).astype(np.float32)
        
        # Add temperature variations for different body parts
        for part_name, bbox in body_parts.items():
            x1, y1, x2, y2 = bbox
            
            # Ensure coordinates are within bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            # Different temperatures for different parts
            if 'udder' in part_name.lower():
                # Slightly elevated for udder (simulate potential issue)
                thermal_data[y1:y2, x1:x2] = np.random.normal(
                    39.0, 0.3, (y2-y1, x2-x1)
                ).astype(np.float32)
            elif 'head' in part_name.lower() or 'nose' in part_name.lower():
                thermal_data[y1:y2, x1:x2] = np.random.normal(
                    38.2, 0.2, (y2-y1, x2-x1)
                ).astype(np.float32)
            elif 'leg' in part_name.lower() or 'hoof' in part_name.lower():
                thermal_data[y1:y2, x1:x2] = np.random.normal(
                    37.8, 0.2, (y2-y1, x2-x1)
                ).astype(np.float32)
        
        print(f"✓ Simulated thermal data: shape {thermal_data.shape}")
        print(f"  Temperature range: {np.min(thermal_data):.1f}°C - {np.max(thermal_data):.1f}°C")
        
        return thermal_data
    
    def extract_temperature_for_region(self, thermal_array: np.ndarray, 
                                      bbox: list) -> Dict[str, float]:
        """
        Extract temperature statistics for a region
        
        Args:
            thermal_array: Full thermal image array
            bbox: Bounding box [x1, y1, x2, y2]
            
        Returns:
            Dictionary with temperature statistics
        """
        x1, y1, x2, y2 = bbox
        
        # Ensure coordinates are within bounds
        h, w = thermal_array.shape
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            return {
                'temp_mean': 0.0,
                'temp_max': 0.0,
                'temp_min': 0.0,
                'temp_std': 0.0
            }
        
        # Extract region
        region = thermal_array[y1:y2, x1:x2]
        
        return {
            'temp_mean': float(np.mean(region)),
            'temp_max': float(np.max(region)),
            'temp_min': float(np.min(region)),
            'temp_std': float(np.std(region))
        }


# Example usage
if __name__ == '__main__':
    parser = FLIRDataParser()
    
    # Test with dummy data
    dummy_json = json.dumps({
        'thermal_array': [[37.5, 37.6], [37.4, 37.7]]
    })
    
    thermal_array = parser.parse_thermal_data(dummy_json)
    if thermal_array is not None:
        print(f"Parsed array:\n{thermal_array}")
        
        is_valid = parser.validate_thermal_data(thermal_array)
        print(f"Valid: {is_valid}")
