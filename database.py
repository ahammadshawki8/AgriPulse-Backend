"""
Database setup and models
SQLite database for cattle health monitoring
"""
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()


class Animal(db.Model):
    """Animal model"""
    __tablename__ = 'animals'
    
    id = db.Column(db.String(50), primary_key=True)
    tag_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100))
    breed = db.Column(db.String(50))
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    scans = db.relationship('Scan', backref='animal', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'tag_id': self.tag_id,
            'name': self.name,
            'breed': self.breed,
            'age': self.age,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Scan(db.Model):
    """Scan model"""
    __tablename__ = 'scans'
    
    id = db.Column(db.String(50), primary_key=True)
    animal_id = db.Column(db.String(50), db.ForeignKey('animals.id'), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    image_path = db.Column(db.String(500), nullable=False)
    annotated_image_path = db.Column(db.String(500))
    
    # Relationships
    detections = db.relationship('Detection', backref='scan', lazy=True, cascade='all, delete-orphan')
    temperatures = db.relationship('Temperature', backref='scan', lazy=True, cascade='all, delete-orphan')
    diagnosis = db.relationship('Diagnosis', backref='scan', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self, include_details=False):
        result = {
            'id': self.id,
            'animal_id': self.animal_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'image_path': self.image_path,
            'annotated_image_path': self.annotated_image_path
        }
        
        if include_details:
            result['detections'] = [d.to_dict() for d in self.detections]
            result['temperatures'] = [t.to_dict() for t in self.temperatures]
            if self.diagnosis:
                result['diagnosis'] = self.diagnosis.to_dict()
        
        return result


class Detection(db.Model):
    """Detection model - individual body part detections"""
    __tablename__ = 'detections'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(50), db.ForeignKey('scans.id'), nullable=False)
    label = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    bbox_x1 = db.Column(db.Integer, nullable=False)
    bbox_y1 = db.Column(db.Integer, nullable=False)
    bbox_x2 = db.Column(db.Integer, nullable=False)
    bbox_y2 = db.Column(db.Integer, nullable=False)
    
    def to_dict(self):
        return {
            'label': self.label,
            'confidence': self.confidence,
            'bbox': [self.bbox_x1, self.bbox_y1, self.bbox_x2, self.bbox_y2]
        }


class Temperature(db.Model):
    """Temperature model - temperature readings for body parts"""
    __tablename__ = 'temperatures'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(50), db.ForeignKey('scans.id'), nullable=False)
    body_part = db.Column(db.String(50), nullable=False)
    temp_mean = db.Column(db.Float, nullable=False)
    temp_max = db.Column(db.Float, nullable=False)
    temp_min = db.Column(db.Float, nullable=False)
    temp_std = db.Column(db.Float, nullable=False)
    
    def to_dict(self):
        return {
            'body_part': self.body_part,
            'temp_mean': self.temp_mean,
            'temp_max': self.temp_max,
            'temp_min': self.temp_min,
            'temp_std': self.temp_std
        }


class Diagnosis(db.Model):
    """Diagnosis model - health diagnosis results"""
    __tablename__ = 'diagnoses'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.String(50), db.ForeignKey('scans.id'), nullable=False, unique=True)
    status = db.Column(db.String(50), nullable=False)  # 'healthy' or 'attention_needed'
    alerts = db.Column(db.Text)  # JSON string
    recommendations = db.Column(db.Text)  # JSON string
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'status': self.status,
            'alerts': json.loads(self.alerts) if self.alerts else [],
            'recommendations': json.loads(self.recommendations) if self.recommendations else [],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


def init_db(app):
    """Initialize database"""
    db.init_app(app)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✓ Database initialized")
        
        # Create some test animals if none exist
        if Animal.query.count() == 0:
            test_animals = [
                Animal(id='COW001', tag_id='DC-001', name='Bessie', breed='Holstein', age=3),
                Animal(id='COW002', tag_id='DC-002', name='Daisy', breed='Jersey', age=4),
                Animal(id='COW003', tag_id='DC-003', name='Molly', breed='Holstein', age=2),
                Animal(id='COW004', tag_id='DC-004', name='Bella', breed='Guernsey', age=5),
            ]
            
            for animal in test_animals:
                db.session.add(animal)
            
            db.session.commit()
            print(f"✓ Created {len(test_animals)} test animals")
            
            # Add dummy scan history
            create_dummy_scan_history()


def create_dummy_scan_history():
    """Create dummy scan history for testing"""
    import uuid
    from datetime import datetime, timedelta
    
    # Create dummy scans for COW001 and COW002
    dummy_scans = [
        # COW001 - Recent healthy scans
        {
            'animal_id': 'COW001',
            'days_ago': 1,
            'scenario': 'healthy',
            'body_parts': ['head', 'body', 'udder', 'leg_1', 'leg_2']
        },
        {
            'animal_id': 'COW001', 
            'days_ago': 2,
            'scenario': 'healthy',
            'body_parts': ['head', 'body', 'udder', 'leg_1']
        },
        {
            'animal_id': 'COW001',
            'days_ago': 3, 
            'scenario': 'mastitis_mild',
            'body_parts': ['head', 'body', 'udder', 'leg_1', 'leg_2']
        },
        
        # COW002 - Some health issues
        {
            'animal_id': 'COW002',
            'days_ago': 1,
            'scenario': 'lameness_right',
            'body_parts': ['head', 'body', 'leg_1', 'leg_2', 'leg_3']
        },
        {
            'animal_id': 'COW002',
            'days_ago': 4,
            'scenario': 'healthy', 
            'body_parts': ['head', 'body', 'udder', 'leg_1']
        },
        
        # COW003 - Healthy
        {
            'animal_id': 'COW003',
            'days_ago': 2,
            'scenario': 'healthy',
            'body_parts': ['head', 'body', 'udder']
        }
    ]
    
    for scan_data in dummy_scans:
        scan_id = str(uuid.uuid4())
        timestamp = datetime.utcnow() - timedelta(days=scan_data['days_ago'])
        
        # Create scan
        scan = Scan(
            id=scan_id,
            animal_id=scan_data['animal_id'],
            timestamp=timestamp,
            image_path=f"/dummy/scan_{scan_id}.jpg",
            annotated_image_path=None
        )
        db.session.add(scan)
        
        # Generate thermal data based on scenario
        thermal_data = generate_dummy_thermal_data(scan_data['scenario'], scan_data['body_parts'])
        
        # Create temperature records
        for part_name, temps in thermal_data.items():
            temperature = Temperature(
                scan_id=scan_id,
                body_part=part_name,
                temp_mean=temps['temp_mean'],
                temp_max=temps['temp_max'],
                temp_min=temps['temp_min'],
                temp_std=temps['temp_std']
            )
            db.session.add(temperature)
        
        # Create diagnosis
        diagnosis_result = perform_simple_diagnosis(thermal_data, 22.0, 65.0)
        diagnosis = Diagnosis(
            scan_id=scan_id,
            status=diagnosis_result['status'],
            alerts=json.dumps(diagnosis_result['alerts']),
            recommendations=json.dumps(diagnosis_result['recommendations'])
        )
        db.session.add(diagnosis)
    
    db.session.commit()
    print(f"✓ Created {len(dummy_scans)} dummy scans with thermal data and diagnosis")


def generate_dummy_thermal_data(scenario, body_parts):
    """Generate dummy thermal data for testing"""
    import random
    
    # Base temperatures for different scenarios
    scenario_temps = {
        'healthy': {'base': 37.5, 'variation': 1.0},
        'mastitis_mild': {'base': 38.0, 'variation': 1.5, 'udder_boost': 2.2},
        'mastitis_moderate': {'base': 38.2, 'variation': 1.8, 'udder_boost': 3.0},
        'lameness_right': {'base': 37.8, 'variation': 1.2, 'leg_boost': 3.5},
        'fever_mild': {'base': 38.5, 'variation': 1.0, 'head_boost': 1.3}
    }
    
    config = scenario_temps.get(scenario, scenario_temps['healthy'])
    base_temp = config['base']
    variation = config['variation']
    
    thermal_data = {}
    
    for part_name in body_parts:
        part_base_temp = base_temp
        
        # Apply scenario-specific boosts
        if 'udder' in part_name.lower() and 'udder_boost' in config:
            part_base_temp += config['udder_boost']
        elif 'leg' in part_name.lower() and 'leg_boost' in config:
            part_base_temp += config['leg_boost']
        elif any(head_part in part_name.lower() for head_part in ['head', 'eye', 'ear']) and 'head_boost' in config:
            part_base_temp += config['head_boost']
        
        # Generate realistic temperature stats
        temp_mean = part_base_temp + random.uniform(-0.3, 0.3)
        temp_std = variation * random.uniform(0.5, 1.5)
        temp_min = max(25.0, temp_mean - temp_std * 1.5)
        temp_max = min(45.0, temp_mean + temp_std * 2.0)
        
        thermal_data[part_name] = {
            'temp_mean': round(temp_mean, 2),
            'temp_max': round(temp_max, 2),
            'temp_min': round(temp_min, 2),
            'temp_std': round(temp_std, 2)
        }
    
    return thermal_data


def get_or_create_animal(animal_id, tag_id=None):
    """Get existing animal or create new one"""
    animal = Animal.query.get(animal_id)
    
    if not animal and tag_id:
        animal = Animal(id=animal_id, tag_id=tag_id)
        db.session.add(animal)
        db.session.commit()
    
    return animal
