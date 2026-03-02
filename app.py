"""
Flask Backend for FLIR Cattle Health Monitoring System
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from pathlib import Path
import config
from database import db, init_db

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(config)

# Enable CORS
CORS(app, origins=config.CORS_ORIGINS)

# Initialize database
init_db(app)

# Helper function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


# ============================================================================
# ROUTES
# ============================================================================

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'FLIR Cattle Health Monitoring API is running',
        'version': '1.0.0'
    }), 200


@app.route('/api/test', methods=['GET'])
def test():
    """Test endpoint"""
    return jsonify({
        'message': 'API is working!',
        'upload_folder': str(config.UPLOAD_FOLDER),
        'result_folder': str(config.RESULT_FOLDER)
    }), 200


@app.route('/api/analyze', methods=['POST'])
def analyze_image():
    """
    Analyze cattle image endpoint - WITH GROUNDING DINO
    
    Workflow Step 1: Receive image and thermal data from frontend
    Backend runs Grounding DINO detection and returns body part coordinates
    
    Accepts:
        - image: File (JPEG/PNG)
        - thermal_data: JSON (thermal array from FLIR camera) - optional
        - animal_id: String (optional)
    
    Returns:
        - scan_id: Unique identifier
        - timestamp: Analysis timestamp
        - body_parts: Dict of body part coordinates {part_name: [x1, y1, x2, y2]}
        - detections: List of all detections with confidence scores
        - message: Success message
    """
    import uuid
    from datetime import datetime
    from services.detection_service_hf_space import detect_body_parts
    from database import db, Scan, Detection, get_or_create_animal
    
    # Check if image file is present
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file is allowed
    if not allowed_file(file.filename):
        return jsonify({
            'error': f'Invalid file type. Allowed types: {", ".join(config.ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Generate unique scan ID
        scan_id = str(uuid.uuid4())
        timestamp = datetime.now()
        
        # Secure filename and save
        filename = secure_filename(file.filename)
        file_ext = filename.rsplit('.', 1)[1].lower()
        saved_filename = f"scan_{scan_id}.{file_ext}"
        file_path = config.UPLOAD_FOLDER / saved_filename
        
        file.save(str(file_path))
        
        # Get optional parameters
        thermal_data = request.form.get('thermal_data', None)
        animal_id = request.form.get('animal_id', None)
        
        # Log upload
        print(f"\n{'='*70}")
        print(f"NEW SCAN REQUEST")
        print(f"{'='*70}")
        print(f"✓ Image uploaded: {saved_filename}")
        print(f"  Scan ID: {scan_id}")
        print(f"  Animal ID: {animal_id or 'Not provided'}")
        print(f"  Thermal data: {'Provided' if thermal_data else 'Not provided'}")
        
        # Run Grounding DINO detection
        print(f"\n[1/4] Running Grounding DINO detection...")
        
        # Use HF API if token is set, otherwise use local model
        hf_token = os.environ.get('HUGGINGFACE_API_TOKEN')
        if hf_token:
            print(f"[Detection] Using Hugging Face Inference API")
            from services.detection_service_hf_api import detect_body_parts
        else:
            print(f"[Detection] Using HuggingFace Space")
            from services.detection_service_hf_space import detect_body_parts
        
        detections, body_parts = detect_body_parts(str(file_path))
        
        print(f"✓ Detected {len(detections)} body parts")
        print(f"✓ Grouped into {len(body_parts)} regions: {', '.join(body_parts.keys())}")
        
        # Log detections
        print(f"\n[2/4] Detection results:")
        for part_name, bbox in body_parts.items():
            print(f"  {part_name}: {bbox}")
        
        # Generate annotated image
        print(f"\n[3/4] Generating annotated image...")
        from services.visualization_service import draw_detections
        annotated_path = draw_detections(str(file_path), detections, body_parts)
        print(f"✓ Annotated image saved: {annotated_path}")
        
        # Save to database
        print(f"\n[4/4] Saving to database...")
        
        # Create scan record
        scan = Scan(
            id=scan_id,
            animal_id=animal_id,
            timestamp=timestamp,
            image_path=str(file_path),
            annotated_image_path=str(annotated_path)
        )
        db.session.add(scan)
        
        # Save detections
        for det in detections:
            detection = Detection(
                scan_id=scan_id,
                label=det['label'],
                confidence=det['confidence'],
                bbox_x1=det['bbox'][0],
                bbox_y1=det['bbox'][1],
                bbox_x2=det['bbox'][2],
                bbox_y2=det['bbox'][3]
            )
            db.session.add(detection)
        
        db.session.commit()
        print(f"✓ Saved scan and {len(detections)} detections to database")
        
        print(f"\n{'='*70}\n")
        
        return jsonify({
            'success': True,
            'scan_id': scan_id,
            'timestamp': timestamp.isoformat(),
            'animal_id': animal_id,
            'body_parts': body_parts,
            'detections': detections,
            'image_path': str(file_path),
            'annotated_image_path': str(annotated_path),
            'message': 'Body parts detected successfully. Use /api/diagnose to analyze temperatures.'
        }), 200
        
    except Exception as e:
        print(f"✗ Error analyzing image: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'error': 'Failed to analyze image',
            'details': str(e)
        }), 500


@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    """
    Enhanced cattle health diagnosis based on research (2020-2025)
    
    Workflow Step 2: Frontend extracts temperatures from thermal data using coordinates
    Frontend sends temperatures to backend for diagnosis
    
    Accepts:
        - scan_id: String (from /api/analyze response)
        - temperatures: Dict of body part temperatures
            {
                'head': {'temp_mean': 38.2, 'temp_max': 38.5, 'temp_min': 37.9, 'temp_std': 0.2},
                'udder': {'temp_mean': 38.7, 'temp_max': 39.1, 'temp_min': 38.3, 'temp_std': 0.3}
            }
        - ambient_temp: Float (optional, default 20.0°C) - for THI calculation
        - relative_humidity: Float (optional, default 50%) - for THI calculation
        - use_baseline: Boolean (optional, default True) - use per-animal baseline
    
    Returns:
        - scan_id: Scan identifier
        - diagnosis: Health diagnosis with status, alerts, recommendations, confidence
        - message: Success message
    """
    import json
    from datetime import datetime
    from services.diagnosis_service_v2 import diagnose_health_v2
    from database import db, Scan, Temperature, Diagnosis
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        scan_id = data.get('scan_id')
        temperatures = data.get('temperatures')
        ambient_temp = data.get('ambient_temp', 20.0)
        relative_humidity = data.get('relative_humidity', 50.0)
        use_baseline = data.get('use_baseline', True)
        
        if not scan_id:
            return jsonify({'error': 'scan_id is required'}), 400
        
        if not temperatures:
            return jsonify({'error': 'temperatures is required'}), 400
        
        # Check if scan exists
        scan = Scan.query.get(scan_id)
        if not scan:
            return jsonify({'error': f'Scan {scan_id} not found'}), 404
        
        # Get animal_id from scan
        animal_id = scan.animal_id if scan.animal_id else 1  # Default to animal 1
        
        print(f"\n{'='*70}")
        print(f"ENHANCED DIAGNOSIS REQUEST (Research-backed)")
        print(f"{'='*70}")
        print(f"Scan ID: {scan_id}")
        print(f"Animal ID: {animal_id}")
        print(f"Body parts: {', '.join(temperatures.keys())}")
        print(f"Ambient temp: {ambient_temp}°C")
        print(f"Humidity: {relative_humidity}%")
        print(f"Use baseline: {use_baseline}")
        
        # Save temperature readings to database
        print(f"\n[1/3] Saving temperature readings...")
        for body_part, temp_data in temperatures.items():
            temperature = Temperature(
                scan_id=scan_id,
                body_part=body_part,
                temp_mean=temp_data['temp_mean'],
                temp_max=temp_data['temp_max'],
                temp_min=temp_data['temp_min'],
                temp_std=temp_data['temp_std']
            )
            db.session.add(temperature)
        
        print(f"✓ Saved {len(temperatures)} temperature readings")
        
        # Run enhanced diagnosis
        print(f"\n[2/3] Running enhanced health diagnosis...")
        diagnosis_result = diagnose_health_v2(
            animal_id=animal_id,
            temperatures=temperatures,
            ambient_temp=ambient_temp,
            relative_humidity=relative_humidity,
            use_baseline=use_baseline
        )
        
        print(f"✓ Status: {diagnosis_result['status']}")
        print(f"✓ Confidence: {diagnosis_result['confidence']*100:.1f}%")
        print(f"✓ THI: {diagnosis_result['thi']:.1f} {'(Heat Stress)' if diagnosis_result['heat_stress'] else ''}")
        print(f"✓ Baseline used: {diagnosis_result['baseline_used']}")
        print(f"✓ Alerts: {len(diagnosis_result['alerts'])}")
        print(f"✓ Recommendations: {len(diagnosis_result['recommendations'])}")
        
        # Save diagnosis to database
        print(f"\n[3/3] Saving diagnosis...")
        diagnosis = Diagnosis(
            scan_id=scan_id,
            status=diagnosis_result['status'],
            alerts=json.dumps(diagnosis_result['alerts']),
            recommendations=json.dumps(diagnosis_result['recommendations'])
        )
        db.session.add(diagnosis)
        db.session.commit()
        
        print(f"✓ Diagnosis saved to database")
        print(f"\n{'='*70}\n")
        
        return jsonify({
            'success': True,
            'scan_id': scan_id,
            'diagnosis': diagnosis_result,
            'message': 'Enhanced diagnosis completed successfully'
        }), 200
        
    except Exception as e:
        print(f"✗ Error during diagnosis: {str(e)}")
        import traceback
        traceback.print_exc()
        db.session.rollback()
        return jsonify({
            'error': 'Failed to diagnose',
            'details': str(e)
        }), 500


@app.route('/api/animals', methods=['GET'])
def get_animals():
    """
    Get all animals
    
    Returns:
        List of animals with their details
    """
    from database import Animal
    
    try:
        animals = Animal.query.all()
        return jsonify({
            'success': True,
            'animals': [animal.to_dict() for animal in animals],
            'count': len(animals)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch animals',
            'details': str(e)
        }), 500


@app.route('/api/animals/<animal_id>/scans', methods=['GET'])
def get_animal_scans(animal_id):
    """
    Get scan history for an animal
    
    Args:
        animal_id: Animal identifier
    
    Returns:
        List of scans for the animal
    """
    from database import Scan
    
    try:
        scans = Scan.query.filter_by(animal_id=animal_id).order_by(Scan.timestamp.desc()).all()
        
        return jsonify({
            'success': True,
            'animal_id': animal_id,
            'scans': [scan.to_dict(include_details=False) for scan in scans],
            'count': len(scans)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch scans',
            'details': str(e)
        }), 500


@app.route('/api/scans/<scan_id>', methods=['GET'])
def get_scan_details(scan_id):
    """
    Get detailed information about a scan
    
    Args:
        scan_id: Scan identifier
    
    Returns:
        Complete scan details including detections, temperatures, and diagnosis
    """
    from database import Scan
    
    try:
        scan = Scan.query.get(scan_id)
        
        if not scan:
            return jsonify({'error': f'Scan {scan_id} not found'}), 404
        
        return jsonify({
            'success': True,
            'scan': scan.to_dict(include_details=True)
        }), 200
    except Exception as e:
        return jsonify({
            'error': 'Failed to fetch scan details',
            'details': str(e)
        }), 500


# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    print("="*70)
    print("FLIR CATTLE HEALTH MONITORING - BACKEND API")
    print("="*70)
    print(f"Upload folder: {config.UPLOAD_FOLDER}")
    print(f"Result folder: {config.RESULT_FOLDER}")
    print(f"Database: {config.DATABASE_PATH}")
    print("="*70)
    print("\nStarting server...")
    print("API Documentation: http://localhost:5000/health")
    print("="*70 + "\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=config.DEBUG
    )
