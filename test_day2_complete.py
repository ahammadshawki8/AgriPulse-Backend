"""
Day 2 Completion Test - Verify all features working
"""
import requests
import json
from pathlib import Path

BASE_URL = 'http://localhost:5000'

def test_health():
    """Test 1: Health check"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f'{BASE_URL}/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'ok'
    
    print("✓ Server is running")
    print(f"  Message: {data['message']}")
    return True


def test_grounding_dino_detection():
    """Test 2: Grounding DINO detection"""
    print("\n" + "="*70)
    print("TEST 2: Grounding DINO Detection")
    print("="*70)
    
    image_path = Path(__file__).parent.parent / 'input' / 'cow1.jpg'
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'animal_id': 'TEST001'}
        
        response = requests.post(f'{BASE_URL}/api/analyze', files=files, data=data)
    
    assert response.status_code == 200
    result = response.json()
    
    # Verify response structure
    assert 'scan_id' in result
    assert 'body_parts' in result
    assert 'detections' in result
    assert 'annotated_image_path' in result
    
    # Verify body parts detected
    body_parts = result['body_parts']
    assert len(body_parts) > 0
    
    # Verify detections
    detections = result['detections']
    assert len(detections) > 0
    
    print(f"✓ Grounding DINO working")
    print(f"  Scan ID: {result['scan_id']}")
    print(f"  Body parts: {len(body_parts)}")
    print(f"  Detections: {len(detections)}")
    print(f"  Parts detected: {', '.join(body_parts.keys())}")
    
    return True


def test_body_part_coordinates():
    """Test 3: Body part coordinates format"""
    print("\n" + "="*70)
    print("TEST 3: Body Part Coordinates Format")
    print("="*70)
    
    image_path = Path(__file__).parent.parent / 'input' / 'cow2.jpg'
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f'{BASE_URL}/api/analyze', files=files)
    
    result = response.json()
    body_parts = result['body_parts']
    
    # Verify coordinate format
    for part_name, bbox in body_parts.items():
        assert isinstance(bbox, list)
        assert len(bbox) == 4
        assert all(isinstance(x, (int, float)) for x in bbox)
        
        x1, y1, x2, y2 = bbox
        assert x2 > x1  # Valid bounding box
        assert y2 > y1
    
    print(f"✓ Coordinates format valid")
    print(f"  Example: head = {body_parts.get('head', 'N/A')}")
    
    return True


def test_detection_confidence():
    """Test 4: Detection confidence scores"""
    print("\n" + "="*70)
    print("TEST 4: Detection Confidence Scores")
    print("="*70)
    
    image_path = Path(__file__).parent.parent / 'input' / 'cow3.jpg'
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f'{BASE_URL}/api/analyze', files=files)
    
    result = response.json()
    detections = result['detections']
    
    # Verify confidence scores
    for det in detections:
        assert 'label' in det
        assert 'confidence' in det
        assert 'bbox' in det
        
        confidence = det['confidence']
        assert 0.0 <= confidence <= 1.0
    
    # Find highest confidence
    max_conf = max(det['confidence'] for det in detections)
    max_det = next(d for d in detections if d['confidence'] == max_conf)
    
    print(f"✓ Confidence scores valid")
    print(f"  Highest: {max_det['label']} = {max_conf:.3f}")
    print(f"  Range: {min(d['confidence'] for d in detections):.3f} - {max_conf:.3f}")
    
    return True


def test_annotated_image_generation():
    """Test 5: Annotated image generation"""
    print("\n" + "="*70)
    print("TEST 5: Annotated Image Generation")
    print("="*70)
    
    image_path = Path(__file__).parent.parent / 'input' / 'cow4.jpg'
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        response = requests.post(f'{BASE_URL}/api/analyze', files=files)
    
    result = response.json()
    
    # Verify annotated image path
    assert 'annotated_image_path' in result
    annotated_path = Path(result['annotated_image_path'])
    
    # Check if file exists
    assert annotated_path.exists()
    assert annotated_path.suffix == '.jpg'
    
    print(f"✓ Annotated image generated")
    print(f"  Path: {annotated_path}")
    print(f"  Size: {annotated_path.stat().st_size / 1024:.1f} KB")
    
    return True


def test_multiple_images():
    """Test 6: Multiple images in sequence"""
    print("\n" + "="*70)
    print("TEST 6: Multiple Images Processing")
    print("="*70)
    
    input_dir = Path(__file__).parent.parent / 'input'
    images = list(input_dir.glob('cow*.jpg'))[:2]  # Test 2 images
    
    results = []
    for img in images:
        with open(img, 'rb') as f:
            files = {'image': f}
            response = requests.post(f'{BASE_URL}/api/analyze', files=files)
            
        assert response.status_code == 200
        results.append(response.json())
    
    # Verify unique scan IDs
    scan_ids = [r['scan_id'] for r in results]
    assert len(scan_ids) == len(set(scan_ids))
    
    print(f"✓ Multiple images processed")
    print(f"  Images: {len(results)}")
    print(f"  Unique scan IDs: {len(set(scan_ids))}")
    
    return True


def run_all_tests():
    """Run all Day 2 completion tests"""
    print("\n" + "="*70)
    print("DAY 2 COMPLETION TESTS")
    print("="*70)
    
    tests = [
        ("Health Check", test_health),
        ("Grounding DINO Detection", test_grounding_dino_detection),
        ("Body Part Coordinates", test_body_part_coordinates),
        ("Detection Confidence", test_detection_confidence),
        ("Annotated Images", test_annotated_image_generation),
        ("Multiple Images", test_multiple_images),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"\n✗ {name} FAILED: {e}")
            failed += 1
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"\nTotal tests: {len(tests)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n✅ ALL DAY 2 TESTS PASSED!")
        print("\n🎉 Day 2 is COMPLETE and ready for Day 3!")
    else:
        print(f"\n✗ {failed} test(s) failed")
    
    print("\n" + "="*70 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
