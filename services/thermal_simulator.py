"""
Enhanced Thermal Data Simulator
Generates realistic thermal patterns for testing without FLIR camera

Lightweight version without numpy for Render deployment
"""
import random
import math
from typing import Dict, Tuple, Optional
import config


def simulate_thermal_extraction(body_parts: Dict, image_path: str) -> Dict[str, Dict[str, float]]:
    """
    Simulate thermal data extraction from detected body parts
    Optimized for low memory usage on Render free tier - NO NUMPY
    
    Args:
        body_parts: Dictionary of body part names to bounding boxes [x1, y1, x2, y2]
        image_path: Path to the image (for logging)
    
    Returns:
        Dictionary of body part thermal statistics
        Format: {
            'body_part_name': {
                'temp_mean': float,
                'temp_max': float, 
                'temp_min': float,
                'temp_std': float
            }
        }
    """
    print(f"[Thermal] Simulating thermal extraction for {len(body_parts)} body parts")
    
    # Use lightweight simulation without creating large arrays
    # This avoids memory issues on Render free tier
    
    # Randomly choose a health scenario for realistic simulation
    scenarios = [
        'healthy', 'healthy', 'healthy',  # 60% healthy
        'mastitis_mild', 'mastitis_moderate',  # 20% mastitis
        'lameness_left', 'lameness_right',     # 20% lameness  
        'fever_mild'                           # 10% fever
    ]
    
    scenario = random.choice(scenarios)
    print(f"[Thermal] Generated scenario: {scenario}")
    
    # Define temperature ranges for different scenarios and body parts
    temp_ranges = {
        'healthy': {'base': 37.5, 'variation': 1.0},
        'mastitis_mild': {'base': 38.0, 'variation': 1.5, 'udder_boost': 2.2},
        'mastitis_moderate': {'base': 38.2, 'variation': 1.8, 'udder_boost': 3.0},
        'lameness_left': {'base': 37.8, 'variation': 1.2, 'leg_boost': 3.5},
        'lameness_right': {'base': 37.8, 'variation': 1.2, 'leg_boost': 3.5},
        'fever_mild': {'base': 38.5, 'variation': 1.0, 'head_boost': 1.3}
    }
    
    scenario_config = temp_ranges.get(scenario, temp_ranges['healthy'])
    base_temp = scenario_config['base']
    variation = scenario_config['variation']
    
    # Extract temperatures from each body part region
    thermal_data = {}
    
    for part_name, bbox in body_parts.items():
        x1, y1, x2, y2 = bbox
        
        # Ensure coordinates are valid
        if x2 <= x1 or y2 <= y1:
            print(f"[Thermal] {part_name:12} → Invalid bbox, skipping")
            continue
        
        # Calculate region size for realistic variation
        region_area = (x2 - x1) * (y2 - y1)
        size_factor = min(1.0, region_area / 10000)  # Normalize to reasonable range
        
        # Generate realistic temperatures for this body part
        part_base_temp = base_temp
        
        # Apply scenario-specific temperature boosts
        if 'udder' in part_name.lower() and 'udder_boost' in scenario_config:
            part_base_temp += scenario_config['udder_boost']
        elif 'leg' in part_name.lower() and 'leg_boost' in scenario_config:
            part_base_temp += scenario_config['leg_boost']
        elif any(head_part in part_name.lower() for head_part in ['head', 'eye', 'ear']) and 'head_boost' in scenario_config:
            part_base_temp += scenario_config['head_boost']
        
        # Generate temperature statistics without creating large arrays
        # Simulate realistic temperature distribution
        temp_mean = part_base_temp + random.uniform(-0.3, 0.3)
        temp_std = variation * size_factor * random.uniform(0.5, 1.5)
        temp_min = temp_mean - temp_std * 1.5
        temp_max = temp_mean + temp_std * 2.0
        
        # Ensure realistic temperature bounds (25-45°C)
        temp_min = max(25.0, temp_min)
        temp_max = min(45.0, temp_max)
        temp_mean = (temp_min + temp_max) / 2.0
        
        thermal_data[part_name] = {
            'temp_mean': round(temp_mean, 2),
            'temp_max': round(temp_max, 2),
            'temp_min': round(temp_min, 2),
            'temp_std': round(temp_std, 2)
        }
        
        print(f"[Thermal] {part_name:12} → Mean: {temp_mean:.1f}°C, Max: {temp_max:.1f}°C, Range: {temp_max-temp_min:.1f}°C")
    
    print(f"[Thermal] ✓ Extracted thermal data for {len(thermal_data)} body parts")
    return thermal_data
