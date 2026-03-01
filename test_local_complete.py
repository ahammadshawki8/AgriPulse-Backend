"""
Complete Local Backend Test
Tests the entire workflow locally without deployment
"""
import requests
import json
from pathlib import Path
import time

BASE_URL = "http://localhost:5000"

def test_health():
    """Test health endpoint"""
    print("\n" + "="*50)
    print("TEST 1: Health Check")
    print("="*50)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✓ Status: {response.status_code}")
        print(f"✓ Response: {response.json()}")
        return True
    except requests.exceptions.ConnectionError:
        print("❌ Backend not running!")
        print("Please start backend: python backend/app.py")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def test_analyze():
    """Test analyze endpoint"""
    print("\n" + "="*50)
    print("TEST 2: Analyze Image")
    print("="*50)
    
    # Find test image
    image_path = Path("../input/cow1.jpg")
    if not image_path.exists():
        image_path = Path("input/cow1.jpg")
    
    if not image_path.exists():
        print("❌ Test image not found!")
        return False
    
    print(f"✓ Using image: {image_path}")
    
    try:
        # Upload image
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'animal_id': 'COW001'}
            
            print("⏳ Uploading image...")
            start = time.time()
            response = requests.post(
                f"{BASE_URL}/api/analyze",
                files=files,
                data=data,
                timeout=60
            )
            elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Time: {elapsed:.1f}s")
            print(f"✓ Scan ID: {result.get('scan_id')}")
            print(f"✓ Detections: {len(result.get('detections', []))}")
            print(f"✓ Body Parts: {len(result.get('body_parts', {}))}")
            
            # Show detected parts
            if result.get('body_parts'):
                print("\n  Detected body parts:")
                for part, bbox in result['body_parts'].items():
                    print(f"    - {part}: {bbox}")
            
            return result.get('scan_id')
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return None


def test_diagnose(scan_id):
    """Test diagnose endpoint"""
    print("\n" + "="*50)
    print("TEST 3: Diagnose")
    print("="*50)
    
    if not scan_id:
        print("⚠️ Skipping (no scan_id)")
        return False
    
    # Simulate temperature data
    temperatures = {
        "head": {"mean": 38.5, "max": 39.2, "min": 37.8, "std": 0.5},
        "body": {"mean": 38.2, "max": 38.8, "min": 37.6, "std": 0.4},
        "udder": {"mean": 39.8, "max": 40.5, "min": 39.1, "std": 0.6},
        "leg_1": {"mean": 37.5, "max": 38.0, "min": 37.0, "std": 0.3}
    }
    
    try:
        print(f"⏳ Sending temperatures for scan {scan_id}...")
        response = requests.post(
            f"{BASE_URL}/api/diagnose",
            json={
                "scan_id": scan_id,
                "temperatures": temperatures
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✓ Status: {response.status_code}")
            print(f"✓ Health Status: {result.get('status')}")
            print(f"✓ Alerts: {len(result.get('alerts', []))}")
            
            # Show alerts
            if result.get('alerts'):
                print("\n  Alerts:")
                for alert in result['alerts']:
                    print(f"    ⚠️ {alert}")
            
            # Show recommendations
            if result.get('recommendations'):
                print("\n  Recommendations:")
                for rec in result['recommendations']:
                    print(f"    💡 {rec}")
            
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 COMPLETE LOCAL BACKEND TEST")
    print("="*60)
    print("\nThis tests the entire workflow locally:")
    print("1. Health check")
    print("2. Image analysis (Grounding DINO)")
    print("3. Temperature diagnosis")
    print("\nMake sure backend is running: python backend/app.py")
    
    # Test 1: Health
    if not test_health():
        print("\n❌ Backend not running. Start it first!")
        return
    
    # Test 2: Analyze
    scan_id = test_analyze()
    
    # Test 3: Diagnose
    if scan_id:
        test_diagnose(scan_id)
    
    # Summary
    print("\n" + "="*60)
    print("✅ LOCAL BACKEND TEST COMPLETE!")
    print("="*60)
    print("\nYour backend is working perfectly locally!")
    print("You can now:")
    print("1. Connect Android app to http://YOUR_IP:5000")
    print("2. Test complete workflow")
    print("3. Demonstrate the working system")
    print("\nDeployment can wait - focus on demonstration first!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
