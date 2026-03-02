"""
Enhanced Thermal Data Simulator
Generates realistic thermal patterns for testing without FLIR camera

Includes:
- Normal healthy patterns
- Mastitis patterns (elevated udder)
- Lameness patterns (hoof asymmetry)
- Fever patterns (elevated eye)
- Environmental variations
"""
import numpy as np
from typing import Dict, Tuple, Optional
import config


class ThermalSimulator:
    """Generate realistic thermal data for cattle"""
    
    def __init__(self, width: int = 640, height: int = 480):
        self.width = width
        self.height = height
        
    def generate_healthy(self, ambient_temp: float = 20.0) -> np.ndarray:
        """
        Generate thermal data for healthy cow
        
        Args:
            ambient_temp: Ambient temperature (affects surface temps)
        
        Returns:
            2D array of temperatures (Celsius)
        """
        # Base temperature adjusted for ambient
        base_temp = 34.0 + (ambient_temp - 20.0) * 0.1
        
        # Create base thermal image with gradient
        thermal = np.random.normal(base_temp, 0.5, (self.height, self.width))
        
        # Add natural variations
        # Warmer in center (body core)
        y_center, x_center = self.height // 2, self.width // 2
        for y in range(self.height):
            for x in range(self.width):
                dist_from_center = np.sqrt((x - x_center)**2 + (y - y_center)**2)
                thermal[y, x] += 1.0 * np.exp(-dist_from_center / 200)
        
        # Cooler at extremities (legs, tail)
        thermal[:self.height//4, :] -= 2.0  # Top (head area)
        thermal[3*self.height//4:, :] -= 3.0  # Bottom (legs)
        
        # Ensure realistic range (27-38°C)
        thermal = np.clip(thermal, 27.0, 38.0)
        
        return thermal
    
    def generate_mastitis(self, ambient_temp: float = 20.0, 
                          severity: str = 'moderate') -> np.ndarray:
        """
        Generate thermal data with mastitis pattern
        
        Args:
            ambient_temp: Ambient temperature
            severity: 'mild', 'moderate', 'severe'
        
        Returns:
            2D array with elevated udder temperature
        """
        # Start with healthy pattern
        thermal = self.generate_healthy(ambient_temp)
        
        # Define udder region (lower center)
        udder_y_start = int(self.height * 0.6)
        udder_y_end = int(self.height * 0.8)
        udder_x_start = int(self.width * 0.35)
        udder_x_end = int(self.width * 0.65)
        
        # Temperature elevation based on severity
        elevation = {
            'mild': 2.2,      # Just above threshold (2.1°C)
            'moderate': 3.0,  # Clear mastitis
            'severe': 4.5     # Severe infection
        }[severity]
        
        # Add hot spot in udder region
        for y in range(udder_y_start, udder_y_end):
            for x in range(udder_x_start, udder_x_end):
                # Gaussian hot spot
                center_y = (udder_y_start + udder_y_end) // 2
                center_x = (udder_x_start + udder_x_end) // 2
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                thermal[y, x] += elevation * np.exp(-dist / 50)
        
        # Add some asymmetry (one quarter hotter)
        quarter_x = (udder_x_start + udder_x_end) // 2
        thermal[udder_y_start:udder_y_end, quarter_x:udder_x_end] += 0.5
        
        return thermal
    
    def generate_lameness(self, ambient_temp: float = 20.0,
                         affected_side: str = 'right',
                         severity: str = 'moderate') -> np.ndarray:
        """
        Generate thermal data with lameness pattern (hoof asymmetry)
        
        Args:
            ambient_temp: Ambient temperature
            affected_side: 'left' or 'right'
            severity: 'mild', 'moderate', 'severe'
        
        Returns:
            2D array with elevated hoof temperature on one side
        """
        thermal = self.generate_healthy(ambient_temp)
        
        # Define hoof regions (bottom corners)
        hoof_y_start = int(self.height * 0.85)
        hoof_y_end = self.height
        
        left_hoof_x_start = int(self.width * 0.2)
        left_hoof_x_end = int(self.width * 0.4)
        
        right_hoof_x_start = int(self.width * 0.6)
        right_hoof_x_end = int(self.width * 0.8)
        
        # Temperature elevation based on severity
        elevation = {
            'mild': 2.6,      # Just above threshold (2.5°C)
            'moderate': 3.5,  # Clear lameness
            'severe': 5.0     # Severe infection
        }[severity]
        
        # Elevate affected hoof
        if affected_side == 'right':
            x_start, x_end = right_hoof_x_start, right_hoof_x_end
        else:
            x_start, x_end = left_hoof_x_start, left_hoof_x_end
        
        for y in range(hoof_y_start, hoof_y_end):
            for x in range(x_start, x_end):
                center_y = (hoof_y_start + hoof_y_end) // 2
                center_x = (x_start + x_end) // 2
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                thermal[y, x] += elevation * np.exp(-dist / 30)
        
        return thermal
    
    def generate_fever(self, ambient_temp: float = 20.0,
                      severity: str = 'moderate') -> np.ndarray:
        """
        Generate thermal data with fever pattern (elevated eye/head)
        
        Args:
            ambient_temp: Ambient temperature
            severity: 'mild', 'moderate', 'severe'
        
        Returns:
            2D array with elevated head/eye temperature
        """
        thermal = self.generate_healthy(ambient_temp)
        
        # Define head/eye region (top center)
        head_y_start = int(self.height * 0.1)
        head_y_end = int(self.height * 0.3)
        head_x_start = int(self.width * 0.4)
        head_x_end = int(self.width * 0.6)
        
        # Temperature elevation based on severity
        elevation = {
            'mild': 1.3,      # Just above threshold (1.2°C)
            'moderate': 2.0,  # Clear fever
            'severe': 3.0     # High fever
        }[severity]
        
        # Elevate head region
        for y in range(head_y_start, head_y_end):
            for x in range(head_x_start, head_x_end):
                center_y = (head_y_start + head_y_end) // 2
                center_x = (head_x_start + head_x_end) // 2
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                thermal[y, x] += elevation * np.exp(-dist / 40)
        
        return thermal
    
    def generate_stress(self, ambient_temp: float = 20.0) -> np.ndarray:
        """
        Generate thermal data with stress pattern (cold muzzle)
        
        Args:
            ambient_temp: Ambient temperature
        
        Returns:
            2D array with decreased muzzle temperature
        """
        thermal = self.generate_healthy(ambient_temp)
        
        # Define muzzle region (top center, small area)
        muzzle_y_start = int(self.height * 0.15)
        muzzle_y_end = int(self.height * 0.25)
        muzzle_x_start = int(self.width * 0.45)
        muzzle_x_end = int(self.width * 0.55)
        
        # Temperature drop (vasoconstriction)
        drop = 2.5  # >2.0°C drop indicates stress
        
        # Cool muzzle region
        for y in range(muzzle_y_start, muzzle_y_end):
            for x in range(muzzle_x_start, muzzle_x_end):
                center_y = (muzzle_y_start + muzzle_y_end) // 2
                center_x = (muzzle_x_start + muzzle_x_end) // 2
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                thermal[y, x] -= drop * np.exp(-dist / 20)
        
        return thermal
    
    def generate_multiple_issues(self, ambient_temp: float = 20.0) -> np.ndarray:
        """
        Generate thermal data with multiple health issues
        (Realistic scenario - sick cow often has multiple problems)
        
        Returns:
            2D array with mastitis + lameness pattern
        """
        # Start with mastitis
        thermal = self.generate_mastitis(ambient_temp, severity='moderate')
        
        # Add lameness on right side
        hoof_y_start = int(self.height * 0.85)
        hoof_y_end = self.height
        right_hoof_x_start = int(self.width * 0.6)
        right_hoof_x_end = int(self.width * 0.8)
        
        elevation = 3.0
        for y in range(hoof_y_start, hoof_y_end):
            for x in range(right_hoof_x_start, right_hoof_x_end):
                center_y = (hoof_y_start + hoof_y_end) // 2
                center_x = (right_hoof_x_start + right_hoof_x_end) // 2
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                thermal[y, x] += elevation * np.exp(-dist / 30)
        
        return thermal
    
    def add_environmental_noise(self, thermal: np.ndarray, 
                               noise_level: float = 0.3) -> np.ndarray:
        """
        Add realistic environmental noise to thermal data
        
        Args:
            thermal: Base thermal array
            noise_level: Amount of noise (0.0 - 1.0)
        
        Returns:
            Thermal array with noise
        """
        noise = np.random.normal(0, noise_level, thermal.shape)
        return thermal + noise
    
    def generate_scenario(self, scenario: str, 
                         ambient_temp: float = 20.0,
                         add_noise: bool = True) -> Tuple[np.ndarray, str]:
        """
        Generate thermal data for a specific test scenario
        
        Args:
            scenario: 'healthy', 'mastitis', 'lameness', 'fever', 'stress', 'multiple'
            ambient_temp: Ambient temperature
            add_noise: Whether to add environmental noise
        
        Returns:
            Tuple of (thermal_array, description)
        """
        scenarios = {
            'healthy': (
                self.generate_healthy(ambient_temp),
                "Healthy cow - all temperatures normal"
            ),
            'mastitis_mild': (
                self.generate_mastitis(ambient_temp, 'mild'),
                "Mild mastitis - udder temperature +2.2°C"
            ),
            'mastitis_moderate': (
                self.generate_mastitis(ambient_temp, 'moderate'),
                "Moderate mastitis - udder temperature +3.0°C"
            ),
            'mastitis_severe': (
                self.generate_mastitis(ambient_temp, 'severe'),
                "Severe mastitis - udder temperature +4.5°C"
            ),
            'lameness_left': (
                self.generate_lameness(ambient_temp, 'left', 'moderate'),
                "Lameness (left hoof) - asymmetry +3.5°C"
            ),
            'lameness_right': (
                self.generate_lameness(ambient_temp, 'right', 'moderate'),
                "Lameness (right hoof) - asymmetry +3.5°C"
            ),
            'fever_mild': (
                self.generate_fever(ambient_temp, 'mild'),
                "Mild fever - eye temperature +1.3°C"
            ),
            'fever_moderate': (
                self.generate_fever(ambient_temp, 'moderate'),
                "Moderate fever/BRD - eye temperature +2.0°C"
            ),
            'stress': (
                self.generate_stress(ambient_temp),
                "Acute stress - muzzle temperature -2.5°C"
            ),
            'multiple': (
                self.generate_multiple_issues(ambient_temp),
                "Multiple issues - mastitis + lameness"
            )
        }
        
        if scenario not in scenarios:
            scenario = 'healthy'
        
        thermal, description = scenarios[scenario]
        
        if add_noise:
            thermal = self.add_environmental_noise(thermal, 0.3)
        
        return thermal, description


def generate_test_dataset(output_dir: str = 'test_thermal_data'):
    """
    Generate a complete test dataset with all scenarios
    
    Args:
        output_dir: Directory to save thermal data files
    """
    import os
    from pathlib import Path
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    simulator = ThermalSimulator()
    
    scenarios = [
        'healthy',
        'mastitis_mild', 'mastitis_moderate', 'mastitis_severe',
        'lameness_left', 'lameness_right',
        'fever_mild', 'fever_moderate',
        'stress',
        'multiple'
    ]
    
    print(f"Generating test thermal dataset...")
    print(f"Output directory: {output_path}")
    print(f"Scenarios: {len(scenarios)}")
    print("="*70)
    
    for scenario in scenarios:
        thermal, description = simulator.generate_scenario(scenario)
        
        # Save as numpy file
        filename = f"{scenario}.npy"
        filepath = output_path / filename
        np.save(filepath, thermal)
        
        print(f"✓ {scenario:20} → {filename}")
        print(f"  {description}")
        print(f"  Shape: {thermal.shape}, Range: {thermal.min():.1f} - {thermal.max():.1f}°C")
        print()
    
    print("="*70)
    print(f"✓ Generated {len(scenarios)} thermal test files")
    print(f"✓ Location: {output_path.absolute()}")
    print("\nUsage:")
    print("  thermal_data = np.load('test_thermal_data/mastitis_moderate.npy')")


if __name__ == '__main__':
    # Generate test dataset
    generate_test_dataset()
