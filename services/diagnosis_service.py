"""
Diagnosis Service - Health diagnosis based on temperature analysis
"""
import config
from typing import Dict, List, Tuple


class HealthAlert:
    """Health alert for abnormal temperature"""
    def __init__(self, part: str, issue: str, value: float, normal_range: Tuple[float, float], deviation: float):
        self.part = part
        self.issue = issue
        self.value = value
        self.normal_range = normal_range
        self.deviation = deviation
    
    def to_dict(self):
        return {
            'part': self.part,
            'issue': self.issue,
            'value': self.value,
            'normal_range': list(self.normal_range),
            'deviation': self.deviation
        }


def diagnose_health(temperatures: Dict[str, Dict[str, float]]) -> Dict:
    """
    Diagnose cattle health based on temperature readings
    
    Args:
        temperatures: Dict of body part temperatures
            {
                'head': {'temp_mean': 38.2, 'temp_max': 38.5, 'temp_min': 37.9, 'temp_std': 0.2},
                'udder': {'temp_mean': 38.7, 'temp_max': 39.1, 'temp_min': 38.3, 'temp_std': 0.3}
            }
    
    Returns:
        Diagnosis dict with status, alerts, and recommendations
    """
    alerts = []
    recommendations = []
    
    # Check each body part against normal ranges
    for part, temp_data in temperatures.items():
        temp_mean = temp_data['temp_mean']
        
        # Get normal range for this body part
        normal_range = get_normal_range(part)
        
        if normal_range:
            min_temp, max_temp = normal_range
            
            # Check if temperature is outside normal range
            if temp_mean < min_temp:
                deviation = min_temp - temp_mean
                alerts.append(HealthAlert(
                    part=part,
                    issue='low_temperature',
                    value=temp_mean,
                    normal_range=normal_range,
                    deviation=deviation
                ))
                recommendations.append(
                    f"Low {part} temperature ({temp_mean:.1f}°C). "
                    f"Normal range: {min_temp}-{max_temp}°C. "
                    f"Possible poor circulation or hypothermia. Monitor closely."
                )
            
            elif temp_mean > max_temp:
                deviation = temp_mean - max_temp
                alerts.append(HealthAlert(
                    part=part,
                    issue='elevated_temperature',
                    value=temp_mean,
                    normal_range=normal_range,
                    deviation=deviation
                ))
                
                # Specific recommendations based on body part
                if part in ['udder', 'cow udder']:
                    recommendations.append(
                        f"Elevated udder temperature ({temp_mean:.1f}°C). "
                        f"Normal range: {min_temp}-{max_temp}°C. "
                        f"Possible mastitis. Recommend veterinary examination and milk culture test."
                    )
                elif part in ['hoof', 'cow hoof', 'leg', 'cow leg']:
                    recommendations.append(
                        f"Elevated {part} temperature ({temp_mean:.1f}°C). "
                        f"Normal range: {min_temp}-{max_temp}°C. "
                        f"Possible lameness or hoof infection. Check for injuries or swelling."
                    )
                elif part in ['head', 'cow head', 'nose', 'cow nose']:
                    recommendations.append(
                        f"Elevated head temperature ({temp_mean:.1f}°C). "
                        f"Normal range: {min_temp}-{max_temp}°C. "
                        f"Possible fever or respiratory infection. Monitor for other symptoms."
                    )
                else:
                    recommendations.append(
                        f"Elevated {part} temperature ({temp_mean:.1f}°C). "
                        f"Normal range: {min_temp}-{max_temp}°C. "
                        f"Possible inflammation or infection. Recommend veterinary consultation."
                    )
    
    # Determine overall status
    if len(alerts) == 0:
        status = 'healthy'
        recommendations.append("All temperature readings are within normal ranges. Animal appears healthy.")
    else:
        status = 'attention_needed'
    
    return {
        'status': status,
        'alerts': [f"{alert.part}: {alert.issue} ({alert.value:.1f}°C)" for alert in alerts],
        'recommendations': recommendations
    }


def get_normal_range(body_part: str) -> Tuple[float, float]:
    """
    Get normal temperature range for a body part
    
    Args:
        body_part: Name of body part (e.g., 'head', 'udder', 'leg')
    
    Returns:
        Tuple of (min_temp, max_temp) or None if not defined
    """
    # Normalize body part name (remove 'cow' prefix if present)
    part_normalized = body_part.lower().replace('cow ', '').strip()
    
    # Map similar parts
    part_mapping = {
        'nose': 'head',
        'eye': 'head',
        'ear': 'head',
        'hoof': 'leg',
        'body': 'body',
        'neck': 'body',
        'tail': 'body'
    }
    
    # Get mapped part or use original
    part_key = part_mapping.get(part_normalized, part_normalized)
    
    # Return normal range from config
    return config.NORMAL_TEMP_RANGES.get(part_key)


def calculate_temperature_stats(thermal_data: List[List[float]], bbox: List[int]) -> Dict[str, float]:
    """
    Calculate temperature statistics for a region
    
    Args:
        thermal_data: 2D array of temperature values
        bbox: Bounding box [x1, y1, x2, y2]
    
    Returns:
        Dict with temp_mean, temp_max, temp_min, temp_std
    """
    import numpy as np
    
    x1, y1, x2, y2 = bbox
    
    # Extract region from thermal data
    region = []
    for y in range(y1, y2):
        if y < len(thermal_data):
            for x in range(x1, x2):
                if x < len(thermal_data[y]):
                    region.append(thermal_data[y][x])
    
    if not region:
        # Return default values if region is empty
        return {
            'temp_mean': 37.5,
            'temp_max': 38.0,
            'temp_min': 37.0,
            'temp_std': 0.3
        }
    
    region_array = np.array(region)
    
    return {
        'temp_mean': float(np.mean(region_array)),
        'temp_max': float(np.max(region_array)),
        'temp_min': float(np.min(region_array)),
        'temp_std': float(np.std(region_array))
    }


def generate_simulated_thermal_data(image_width: int, image_height: int) -> List[List[float]]:
    """
    Generate simulated thermal data for testing
    
    Args:
        image_width: Width of image
        image_height: Height of image
    
    Returns:
        2D array of temperature values (Celsius)
    """
    import numpy as np
    
    # Generate random temperatures around normal cattle body temperature
    # Normal range: 37.0-38.5°C
    base_temp = 37.5
    variation = 1.0
    
    thermal_data = np.random.normal(base_temp, variation, (image_height, image_width))
    
    # Add some hot spots (potential issues)
    # Random hot spot 1
    hot_x1 = np.random.randint(0, image_width - 50)
    hot_y1 = np.random.randint(0, image_height - 50)
    thermal_data[hot_y1:hot_y1+50, hot_x1:hot_x1+50] += np.random.uniform(0.5, 1.5)
    
    # Ensure temperatures are realistic (36-40°C)
    thermal_data = np.clip(thermal_data, 36.0, 40.0)
    
    return thermal_data.tolist()
