"""
Response schemas for API endpoints
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from datetime import datetime


@dataclass
class BodyPartDetection:
    """Single body part detection"""
    label: str
    confidence: float
    bbox: List[int]  # [x1, y1, x2, y2]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class TemperatureReading:
    """Temperature statistics for a body part"""
    temp_mean: float
    temp_max: float
    temp_min: float
    temp_std: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class HealthAlert:
    """Health alert for abnormal temperature"""
    part: str
    issue: str
    value: float
    normal_range: Tuple[float, float]
    deviation: float
    
    def to_dict(self):
        return {
            'part': self.part,
            'issue': self.issue,
            'value': self.value,
            'normal_range': list(self.normal_range),
            'deviation': self.deviation
        }


@dataclass
class Diagnosis:
    """Health diagnosis result"""
    timestamp: str
    status: str  # 'healthy' or 'attention_needed'
    alerts: List[HealthAlert]
    recommendations: List[str]
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'status': self.status,
            'alerts': [alert.to_dict() for alert in self.alerts],
            'recommendations': self.recommendations
        }


@dataclass
class AnalysisResponse:
    """Complete analysis response"""
    scan_id: str
    timestamp: str
    animal_id: Optional[str]
    image_path: str
    detections: List[BodyPartDetection]
    body_parts: Dict[str, List[int]]  # {part_name: [x1, y1, x2, y2]}
    temperatures: Dict[str, TemperatureReading]
    diagnosis: Diagnosis
    result_image_url: str
    
    def to_dict(self):
        return {
            'scan_id': self.scan_id,
            'timestamp': self.timestamp,
            'animal_id': self.animal_id,
            'image_path': self.image_path,
            'detections': [det.to_dict() for det in self.detections],
            'body_parts': self.body_parts,
            'temperatures': {
                part: temp.to_dict() 
                for part, temp in self.temperatures.items()
            },
            'diagnosis': self.diagnosis.to_dict(),
            'result_image_url': self.result_image_url
        }


@dataclass
class AnimalInfo:
    """Animal information"""
    id: str
    tag_id: str
    name: Optional[str]
    breed: Optional[str]
    age: Optional[int]
    
    def to_dict(self):
        return asdict(self)


@dataclass
class ScanSummary:
    """Summary of a scan for history"""
    scan_id: str
    timestamp: str
    animal_id: Optional[str]
    status: str
    image_url: str
    
    def to_dict(self):
        return asdict(self)


# Helper functions
def create_success_response(data: dict, message: str = "Success") -> dict:
    """Create a success response"""
    return {
        'success': True,
        'message': message,
        'data': data
    }


def create_error_response(error: str, details: Optional[str] = None) -> dict:
    """Create an error response"""
    response = {
        'success': False,
        'error': error
    }
    if details:
        response['details'] = details
    return response
