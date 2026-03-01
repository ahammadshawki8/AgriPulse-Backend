"""
Comprehensive API test script
"""
import requests
import json
from pathlib import Path

BASE_URL = 'http://localhost:5000'

def test_health_check():
    """Test health check endpoint"""
    print("\n" + "="*70)
    print("TEST 1: Health Check")
    print("="*70)
    
    response = requests.get(f'{BASE_URL}/health')
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'
    print("✓ Health check passed")


def test_image_upload():
    """Test image upload endpoint"""
    print("\n" + "="*70)
    print("TEST 2: Image Upload")
    print("="*70)
    
    image_path = Path(__file__).parent.parent / 'input' / 'cow1.jpg'
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {
            'animal_id': 'COW001'
        }
        
        response = requests.post(f'{BASE_URL}/api/analyze', files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    assert 'scan_id' in response.json()
    print("✓ Image upload passed")
    
    return response.json()['scan_id']


def test_image_upload_with_thermal_data():
    """Test image upload with thermal data"""
    print("\n" + "="*70)
    print("TEST 3: Image Upload with Thermal Data")
    print("="*70)
    
    image_path = Path(__file__).parent.parent / 'input' / 'cow2.jpg'
    
    # Dummy thermal data
    thermal_data = {
        'thermal_array': [
            [37.5, 37.6, 37.4] * 100 for _ in range(100)
        ]
    }
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {
            'animal_id': 'COW002',
            'thermal_data': json.dumps(thermal_data)
        }
        
        response = requests.post(f'{BASE_URL}/api/analyze', files=files, data=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert response.json()['success'] == True
    print("✓ Image upload with thermal data passed")


def test_invalid_file_type():
    """Test upload with invalid file type"""
    print("\n" + "="*70)
    print("TEST 4: Invalid File Type")
    print("="*70)
    
    # Create a dummy text file
    files = {'image': ('test.txt', b'This is not an image', 'text/plain')}
    
    response = requests.post(f'{BASE_URL}/api/analyze', files=files)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 400
    assert 'error' in response.json()
    print("✓ Invalid file type test passed")


def test_no_file():
    """Test upload without file"""
    print("\n" + "="*70)
    print("TEST 5: No File Provided")
    print("="*70)
    
    response = requests.post(f'{BASE_URL}/api/analyze')
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 400
    assert 'error' in response.json()
    print("✓ No file test passed")


def test_all_cow_images():
    """Test upload of all cow images"""
    print("\n" + "="*70)
    print("TEST 6: Upload All Cow Images")
    print("="*70)
    
    input_dir = Path(__file__).parent.parent / 'input'
    cow_images = list(input_dir.glob('cow*.jpg'))
    
    print(f"Found {len(cow_images)} cow images")
    
    for i, image_path in enumerate(cow_images, 1):
        print(f"\nUploading {image_path.name}...")
        
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'animal_id': f'COW{i:03d}'}
            
            response = requests.post(f'{BASE_URL}/api/analyze', files=files, data=data)
        
        assert response.status_code == 200
        print(f"  ✓ {image_path.name} uploaded successfully")
        print(f"    Scan ID: {response.json()['scan_id']}")
    
    print(f"\n✓ All {len(cow_images)} images uploaded successfully")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*70)
    print("RUNNING API TESTS")
    print("="*70)
    
    try:
        test_health_check()
        test_image_upload()
        test_image_upload_with_thermal_data()
        test_invalid_file_type()
        test_no_file()
        test_all_cow_images()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✓")
        print("="*70 + "\n")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to server. Make sure Flask server is running!")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")


if __name__ == '__main__':
    run_all_tests()
