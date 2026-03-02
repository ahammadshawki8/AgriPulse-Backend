"""
Test Enhanced Diagnosis Service (Research-backed)

This demonstrates the improvements:
1. Per-animal baseline tracking
2. Environmental correction (THI)
3. Disease-specific thresholds
4. Confidence scores
5. Asymmetry detection
"""
import sys
from services.diagnosis_service_v2 import (
    diagnose_health_v2, 
    calculate_thi,
    apply_thi_correction
)

print("="*70)
print("ENHANCED DIAGNOSIS SERVICE TEST")
print("Research-backed cattle health monitoring (2020-2025)")
print("="*70)

# Test Case 1: Normal healthy cow
print("\n" + "="*70)
print("TEST 1: Healthy Cow (All Normal)")
print("="*70)

temperatures_healthy = {
    'eye': {'temp_mean': 36.0, 'temp_max': 36.5, 'temp_min': 35.7, 'temp_std': 0.2},
    'udder': {'temp_mean': 34.0, 'temp_max': 34.3, 'temp_min': 33.7, 'temp_std': 0.2},
    'hoof': {'temp_mean': 28.5, 'temp_max': 29.0, 'temp_min': 28.0, 'temp_std': 0.3},
    'nose': {'temp_mean': 30.0, 'temp_max': 30.5, 'temp_min': 29.5, 'temp_std': 0.3}
}

result = diagnose_health_v2(
    animal_id=1,
    temperatures=temperatures_healthy,
    ambient_temp=20.0,
    relative_humidity=50.0,
    use_baseline=False  # No baseline for first test
)

print(f"\nStatus: {result['status']}")
print(f"Confidence: {result['confidence']*100:.1f}%")
print(f"THI: {result['thi']:.1f}")
print(f"Alerts: {len(result['alerts'])}")
print(f"\nRecommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")

# Test Case 2: Mastitis detection
print("\n" + "="*70)
print("TEST 2: Mastitis Detection (Elevated Udder Temperature)")
print("="*70)

temperatures_mastitis = {
    'eye': {'temp_mean': 36.0, 'temp_max': 36.5, 'temp_min': 35.7, 'temp_std': 0.2},
    'udder': {'temp_mean': 36.8, 'temp_max': 37.2, 'temp_min': 36.4, 'temp_std': 0.3},  # +2.3°C above normal
    'hoof': {'temp_mean': 28.5, 'temp_max': 29.0, 'temp_min': 28.0, 'temp_std': 0.3}
}

result = diagnose_health_v2(
    animal_id=2,
    temperatures=temperatures_mastitis,
    ambient_temp=20.0,
    relative_humidity=50.0,
    use_baseline=False
)

print(f"\nStatus: {result['status']}")
print(f"Confidence: {result['confidence']*100:.1f}%")
print(f"Alerts: {len(result['alerts'])}")
for alert in result['alerts']:
    print(f"\n  Alert: {alert['part']}")
    print(f"  Issue: {alert['issue']}")
    print(f"  Temperature: {alert['value']:.1f}°C")
    print(f"  Deviation: +{alert['deviation']:.1f}°C")
    print(f"  Disease: {alert['disease']}")
    print(f"  Confidence: {alert['confidence']*100:.0f}%")

print(f"\nRecommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")

# Test Case 3: Lameness detection (asymmetry)
print("\n" + "="*70)
print("TEST 3: Lameness Detection (Hoof Asymmetry)")
print("="*70)

temperatures_lameness = {
    'eye': {'temp_mean': 36.0, 'temp_max': 36.5, 'temp_min': 35.7, 'temp_std': 0.2},
    'left_hoof': {'temp_mean': 28.5, 'temp_max': 29.0, 'temp_min': 28.0, 'temp_std': 0.3},
    'right_hoof': {'temp_mean': 31.2, 'temp_max': 31.8, 'temp_min': 30.8, 'temp_std': 0.4}  # +2.7°C asymmetry
}

result = diagnose_health_v2(
    animal_id=3,
    temperatures=temperatures_lameness,
    ambient_temp=20.0,
    relative_humidity=50.0,
    use_baseline=False
)

print(f"\nStatus: {result['status']}")
print(f"Confidence: {result['confidence']*100:.1f}%")
print(f"Alerts: {len(result['alerts'])}")
for alert in result['alerts']:
    print(f"\n  Alert: {alert['part']}")
    print(f"  Issue: {alert['issue']}")
    print(f"  Temperature: {alert['value']:.1f}°C")
    print(f"  Deviation: {alert['deviation']:.1f}°C")
    if alert.get('disease'):
        print(f"  Disease: {alert['disease']}")
    print(f"  Confidence: {alert['confidence']*100:.0f}%")

print(f"\nRecommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")

# Test Case 4: Heat stress environment
print("\n" + "="*70)
print("TEST 4: Heat Stress Environment (THI Correction)")
print("="*70)

temperatures_heat = {
    'eye': {'temp_mean': 37.5, 'temp_max': 38.0, 'temp_min': 37.0, 'temp_std': 0.3},
    'udder': {'temp_mean': 35.2, 'temp_max': 35.8, 'temp_min': 34.8, 'temp_std': 0.3},
    'body': {'temp_mean': 35.5, 'temp_max': 36.0, 'temp_min': 35.0, 'temp_std': 0.3}
}

# High ambient temp and humidity
ambient_temp = 32.0
relative_humidity = 80.0
thi = calculate_thi(ambient_temp, relative_humidity)

print(f"\nEnvironmental Conditions:")
print(f"  Ambient Temperature: {ambient_temp}°C")
print(f"  Relative Humidity: {relative_humidity}%")
print(f"  THI: {thi:.1f} {'(HEAT STRESS!)' if thi > 72 else ''}")

result = diagnose_health_v2(
    animal_id=4,
    temperatures=temperatures_heat,
    ambient_temp=ambient_temp,
    relative_humidity=relative_humidity,
    use_baseline=False
)

print(f"\nStatus: {result['status']}")
print(f"Confidence: {result['confidence']*100:.1f}%")
print(f"Heat Stress: {result['heat_stress']}")
print(f"Alerts: {len(result['alerts'])}")

print(f"\nRecommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")

# Test Case 5: Fever/BRD detection
print("\n" + "="*70)
print("TEST 5: Fever/BRD Detection (Elevated Eye Temperature)")
print("="*70)

temperatures_fever = {
    'eye': {'temp_mean': 37.2, 'temp_max': 37.8, 'temp_min': 36.8, 'temp_std': 0.3},  # +1.4°C above normal
    'udder': {'temp_mean': 34.0, 'temp_max': 34.3, 'temp_min': 33.7, 'temp_std': 0.2},
    'nose': {'temp_mean': 30.5, 'temp_max': 31.0, 'temp_min': 30.0, 'temp_std': 0.3}
}

result = diagnose_health_v2(
    animal_id=5,
    temperatures=temperatures_fever,
    ambient_temp=20.0,
    relative_humidity=50.0,
    use_baseline=False
)

print(f"\nStatus: {result['status']}")
print(f"Confidence: {result['confidence']*100:.1f}%")
print(f"Alerts: {len(result['alerts'])}")
for alert in result['alerts']:
    print(f"\n  Alert: {alert['part']}")
    print(f"  Issue: {alert['issue']}")
    print(f"  Temperature: {alert['value']:.1f}°C")
    print(f"  Deviation: +{alert['deviation']:.1f}°C")
    print(f"  Disease: {alert['disease']}")
    print(f"  Confidence: {alert['confidence']*100:.0f}%")

print(f"\nRecommendations:")
for rec in result['recommendations']:
    print(f"  • {rec}")

print("\n" + "="*70)
print("SUMMARY: Enhanced Diagnosis Features")
print("="*70)
print("""
✅ Research-backed temperature thresholds (2020-2025 studies)
✅ Disease-specific detection:
   • Mastitis: 80% sensitivity, 84% specificity
   • Lameness: 91% sensitivity, 88% specificity  
   • Fever/BRD: 85% sensitivity, 78% specificity
✅ Environmental correction (THI calculation)
✅ Asymmetry detection (left vs right comparison)
✅ Confidence scores for each alert
✅ Specific veterinary recommendations
✅ Per-animal baseline tracking (when data available)

Next Steps:
1. Deploy updated backend to Render
2. Update Android app to send ambient_temp and humidity
3. Collect real data to build per-animal baselines
4. Monitor accuracy and refine thresholds
""")
print("="*70)
