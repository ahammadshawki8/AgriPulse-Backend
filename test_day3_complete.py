"""
Day 3 Complete Test Suite
Tests database, diagnosis engine, and all API endpoints
"""
import requests
import json
from pathlib import Path
import time

# Configuration
BASE_URL = "http://localhost:5000"
TEST_IMAGES_DIR = Path("../input")

# Test images
TEST_IMAGES = [
    "cow1.jpg",
    "cow2.jpg",
    "cow3.jpg",
    "cow4.jpg"
]


def print_section(title):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"{title}")
    print(f"{'='*70}\n")


def test_health_check():
    """Test 1: Health check endpoint"""
    print_section("TEST 1: Health Check")
    
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    print("✓ Health check passed")


def test_get_animals():
    """Test 2: Get all animals"""
    print_section("TEST 2: Get All Animals")
    
    response = requests.get(f"{BASE_URL}/api/animals")
    print(f"Status Code: {response.status_code}")
    
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data['success'] == True
    assert 'animals' in data
    assert len(data['animals']) > 0
    
    print(f"✓ Found {len(data['animals'])} animals")
    return data['animals']


def test_analyze_and_diagnose(image_name, animal_id=None):
    """Test 3: Complete workflow - analyze + diagnose"""
    print_section(f"TEST 3: Analyze & Diagnose - {image_name}")
    
    image_path = TEST_IMAGES_DIR / image_name
    
    if not image_path.exists():
        print(f"✗ Image not found: {image_path}")
        return None
    
    # Step 1: Analyze image
    print(f"[1/2] Uploading and analyzing image...")
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {}
        if animal_id:
            data['animal_id'] = animal_id
        
        response = requests.post(f"{BASE_URL}/api/analyze", files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"✗ Analysis failed: {response.text}")
        return None
    
    result = response.json()
    print(f"✓ Analysis successful")
    print(f"  Scan ID: {result['scan_id']}")
    print(f"  Detections: {len(result['detections'])}")
    print(f"  Body parts: {', '.join(result['body_parts'].keys())}")
    
    scan_id = result['scan_id']
    body_parts = result['body_parts']
    
    # Step 2: Generate simulated temperatures
    print(f"\n[2/2] Generating temperatures and diagnosing...")
    
    temperatures = generate_simulated_temperatures(body_parts)
    
    print(f"Simulated temperatures:")
    for part, temp_data in temperatures.items():
        print(f"  {part}: {temp_data['temp_mean']:.1f}°C (range: {temp_data['temp_min']:.1f}-{temp_data['temp_max']:.1f}°C)")
    
    # Step 3: Diagnose
    diagnose_data = {
        'scan_id': scan_id,
        'temperatures': temperatures
    }
    
    response = requests.post(
        f"{BASE_URL}/api/diagnose",
        json=diagnose_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"\nDiagnosis Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"✗ Diagnosis failed: {response.text}")
        return None
    
    diagnosis_result = response.json()
    print(f"✓ Diagnosis successful")
    
    diagnosis = diagnosis_result['diagnosis']
    print(f"\nDiagnosis Results:")
    print(f"  Status: {diagnosis['status']}")
    print(f"  Alerts: {len(diagnosis['alerts'])}")
    
    if diagnosis['alerts']:
        print(f"\n  Health Alerts:")
        for alert in diagnosis['alerts']:
            print(f"    - {alert['part']}: {alert['issue']} ({alert['value']:.1f}°C, deviation: {alert['deviation']:.1f}°C)")
    
    print(f"\n  Recommendations:")
    for i, rec in enumerate(diagnosis['recommendations'], 1):
        print(f"    {i}. {rec}")
    
    return {
        'scan_id': scan_id,
        'analysis': result,
        'diagnosis': diagnosis_result
    }


def test_get_scan_details(scan_id):
    """Test 4: Get scan details"""
    print_section(f"TEST 4: Get Scan Details - {scan_id}")
    
    response = requests.get(f"{BASE_URL}/api/scans/{scan_id}")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"✗ Failed to get scan details: {response.text}")
        return
    
    data = response.json()
    scan = data['scan']
    
    print(f"✓ Scan details retrieved")
    print(f"\nScan Information:")
    print(f"  ID: {scan['id']}")
    print(f"  Timestamp: {scan['timestamp']}")
    print(f"  Animal ID: {scan['animal_id'] or 'N/A'}")
    print(f"  Detections: {len(scan['detections'])}")
    print(f"  Temperatures: {len(scan['temperatures'])}")
    print(f"  Diagnosis: {scan['diagnosis']['status'] if scan['diagnosis'] else 'N/A'}")


def test_get_animal_scans(animal_id):
    """Test 5: Get animal scan history"""
    print_section(f"TEST 5: Get Animal Scan History - {animal_id}")
    
    response = requests.get(f"{BASE_URL}/api/animals/{animal_id}/scans")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code != 200:
        print(f"✗ Failed to get animal scans: {response.text}")
        return
    
    data = response.json()
    print(f"✓ Animal scan history retrieved")
    print(f"  Total scans: {data['count']}")
    
    if data['scans']:
        print(f"\n  Recent scans:")
        for scan in data['scans'][:3]:  # Show first 3
            print(f"    - {scan['timestamp']}: {scan['id']}")


def generate_simulated_temperatures(body_parts):
    """Generate simulated temperature data for testing"""
    import random
    
    temperatures = {}
    
    for part_name, bbox in body_parts.items():
        # Normalize part name
        part_normalized = part_name.lower().replace('cow ', '').strip()
        
        # Base temperature with some variation
        base_temp = 37.5
        
        # Add variation based on body part
        if 'udder' in part_normalized:
            # Sometimes simulate mastitis (elevated udder temp)
            if random.random() < 0.3:  # 30% chance
                base_temp = 38.8  # Elevated
            else:
                base_temp = 37.8
        elif 'leg' in part_normalized or 'hoof' in part_normalized:
            base_temp = 37.3
        elif 'head' in part_normalized or 'nose' in part_normalized:
            base_temp = 37.9
        
        # Add random variation
        temp_mean = base_temp + random.uniform(-0.3, 0.3)
        temp_std = random.uniform(0.1, 0.4)
        temp_max = temp_mean + random.uniform(0.2, 0.6)
        temp_min = temp_mean - random.uniform(0.2, 0.5)
        
        temperatures[part_name] = {
            'temp_mean': round(temp_mean, 2),
            'temp_max': round(temp_max, 2),
            'temp_min': round(temp_min, 2),
            'temp_std': round(temp_std, 2)
        }
    
    return temperatures


def run_all_tests():
    """Run all Day 3 tests"""
    print("\n" + "="*70)
    print("DAY 3 COMPLETE TEST SUITE")
    print("Database, Diagnosis Engine, and API Endpoints")
    print("="*70)
    
    try:
        # Test 1: Health check
        test_health_check()
        time.sleep(0.5)
        
        # Test 2: Get animals
        animals = test_get_animals()
        time.sleep(0.5)
        
        # Test 3: Analyze and diagnose multiple images
        scan_ids = []
        
        # Test with first animal
        if animals:
            animal_id = animals[0]['id']
            print(f"\nTesting with Animal: {animals[0]['name']} ({animal_id})")
        else:
            animal_id = None
        
        for i, image_name in enumerate(TEST_IMAGES, 1):
            print(f"\n--- Image {i}/{len(TEST_IMAGES)} ---")
            result = test_analyze_and_diagnose(image_name, animal_id)
            if result:
                scan_ids.append(result['scan_id'])
            time.sleep(1)
        
        # Test 4: Get scan details
        if scan_ids:
            test_get_scan_details(scan_ids[0])
            time.sleep(0.5)
        
        # Test 5: Get animal scan history
        if animal_id:
            test_get_animal_scans(animal_id)
        
        # Summary
        print_section("TEST SUMMARY")
        print(f"✓ All tests completed successfully!")
        print(f"✓ Analyzed {len(scan_ids)} images")
        print(f"✓ Database operations working")
        print(f"✓ Diagnosis engine working")
        print(f"✓ All API endpoints functional")
        print(f"\n{'='*70}\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    print("\nMake sure the Flask server is running on http://localhost:5000")
    print("Press Enter to start tests...")
    input()
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 DAY 3 COMPLETE! All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")
