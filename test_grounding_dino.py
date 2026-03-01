"""
Test Grounding DINO integration with backend API
"""
import requests
import json
from pathlib import Path
import time

BASE_URL = 'http://localhost:5000'

def test_grounding_dino_detection():
    """Test Grounding DINO detection on all cow images"""
    print("\n" + "="*70)
    print("TESTING GROUNDING DINO INTEGRATION")
    print("="*70)
    
    input_dir = Path(__file__).parent.parent / 'input'
    cow_images = sorted(list(input_dir.glob('cow*.jpg')))
    
    print(f"\nFound {len(cow_images)} cow images to test\n")
    
    results = []
    
    for i, image_path in enumerate(cow_images, 1):
        print(f"\n{'='*70}")
        print(f"TEST {i}/{len(cow_images)}: {image_path.name}")
        print(f"{'='*70}")
        
        # Upload and analyze
        with open(image_path, 'rb') as f:
            files = {'image': f}
            data = {'animal_id': f'COW{i:03d}'}
            
            print(f"Uploading {image_path.name}...")
            start_time = time.time()
            
            response = requests.post(
                f'{BASE_URL}/api/analyze',
                files=files,
                data=data
            )
            
            elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"\n✓ Analysis complete in {elapsed:.2f} seconds")
            print(f"\nScan ID: {result['scan_id']}")
            print(f"Timestamp: {result['timestamp']}")
            
            # Display body parts
            body_parts = result.get('body_parts', {})
            print(f"\nBody Parts Detected: {len(body_parts)}")
            for part_name, bbox in body_parts.items():
                print(f"  {part_name}: {bbox}")
            
            # Display detections
            detections = result.get('detections', [])
            print(f"\nAll Detections: {len(detections)}")
            for det in detections[:5]:  # Show first 5
                print(f"  {det['label']}: {det['confidence']:.3f}")
            if len(detections) > 5:
                print(f"  ... and {len(detections) - 5} more")
            
            results.append({
                'image': image_path.name,
                'success': True,
                'body_parts_count': len(body_parts),
                'detections_count': len(detections),
                'time': elapsed
            })
            
        else:
            print(f"\n✗ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            results.append({
                'image': image_path.name,
                'success': False,
                'error': response.text
            })
    
    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}\n")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"Total images tested: {len(results)}")
    print(f"Successful: {len(successful)}")
    print(f"Failed: {len(failed)}")
    
    if successful:
        avg_time = sum(r['time'] for r in successful) / len(successful)
        avg_parts = sum(r['body_parts_count'] for r in successful) / len(successful)
        avg_detections = sum(r['detections_count'] for r in successful) / len(successful)
        
        print(f"\nAverage processing time: {avg_time:.2f} seconds")
        print(f"Average body parts detected: {avg_parts:.1f}")
        print(f"Average total detections: {avg_detections:.1f}")
    
    if successful:
        print("\n✓ All tests passed!")
        print("\nDetailed Results:")
        for r in successful:
            print(f"  {r['image']}: {r['body_parts_count']} parts, {r['detections_count']} detections, {r['time']:.2f}s")
    
    if failed:
        print("\n✗ Some tests failed:")
        for r in failed:
            print(f"  {r['image']}: {r.get('error', 'Unknown error')}")
    
    print(f"\n{'='*70}\n")
    
    return len(failed) == 0


if __name__ == '__main__':
    success = test_grounding_dino_detection()
    exit(0 if success else 1)
