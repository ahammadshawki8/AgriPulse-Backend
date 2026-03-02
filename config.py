"""
Configuration settings for the Flask backend
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Upload and result directories
UPLOAD_FOLDER = BASE_DIR / 'uploads'
RESULT_FOLDER = BASE_DIR / 'results'
UPLOAD_FOLDER.mkdir(exist_ok=True)
RESULT_FOLDER.mkdir(exist_ok=True)

# Database
# Use PostgreSQL on Render, SQLite locally
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Render provides DATABASE_URL
    # Fix for SQLAlchemy 1.4+ (postgres:// -> postgresql://)
    if DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
else:
    # Local development - use SQLite
    DATABASE_PATH = BASE_DIR / 'cattle_health.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_PATH}'

SQLALCHEMY_TRACK_MODIFICATIONS = False

# File upload settings
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

# Grounding DINO settings
GROUNDING_DINO_MODEL = "IDEA-Research/grounding-dino-tiny"
DETECTION_THRESHOLD = 0.3
TEXT_PROMPT = (
    "cow head. cow nose. cow eye. cow ear. "
    "cow neck. cow body. cow leg. cow hoof. "
    "cow udder. cow tail."
)

# Temperature ranges (Celsius) - Based on veterinary research (2020-2025)
# These are Skin Surface Temperature (SST) ranges, not core body temperature
NORMAL_TEMP_RANGES = {
    # Eye (medial canthus) - Early fever/BRD detection
    'eye': (35.5, 36.8),
    'head': (35.5, 36.8),  # Mapped to eye
    
    # Udder quarters - Mastitis detection
    'udder': (33.4, 34.5),
    
    # Hooves/Legs - Lameness/Digital Dermatitis detection
    'hoof': (27.0, 30.5),
    'leg': (27.0, 30.5),
    
    # Muzzle/Nose - Stress/Pain detection
    'nose': (28.5, 32.0),
    'muzzle': (28.5, 32.0),
    
    # Body/Neck/Tail - General monitoring
    'body': (33.0, 35.0),
    'neck': (33.0, 35.0),
    'tail': (30.0, 33.0)
}

# Disease detection thresholds (temperature elevation in Celsius)
# Based on research: sensitivity 80-92%, specificity 75-85%
DISEASE_THRESHOLDS = {
    'mastitis': {
        'delta_temp': 2.1,  # >+2.1°C above normal indicates subclinical mastitis
        'sensitivity': 0.80,
        'specificity': 0.84
    },
    'lameness': {
        'delta_temp': 2.5,  # >+2.5°C indicates digital dermatitis/lameness
        'asymmetry_threshold': 2.0,  # >2.0°C difference between left/right hooves
        'sensitivity': 0.91,
        'specificity': 0.88
    },
    'fever_brd': {
        'delta_temp': 1.2,  # >+1.2°C in eye indicates early fever/BRD
        'sensitivity': 0.85,
        'specificity': 0.78
    },
    'stress_pain': {
        'delta_temp': -2.0,  # >-2.0°C drop in muzzle indicates acute stress/pain
        'sensitivity': 0.75,
        'specificity': 0.70
    }
}

# FLIR camera settings
FLIR_EMISSIVITY = 0.98  # Standard for biological tissue (not 0.95)

# Environmental correction settings
THI_HEAT_STRESS_THRESHOLD = 72  # Above this, cattle enter heat stress
THI_TEMP_CORRECTION_FACTOR = 0.03  # 0.3°C per 10 THI points

# Baseline tracking settings
BASELINE_WINDOW_DAYS = 7  # Rolling average window for per-animal baseline
BASELINE_STD_MULTIPLIER = 2.0  # Alert if >2 standard deviations above baseline

# Minimum viable accuracy targets
TARGET_SENSITIVITY = 0.85  # 85% - catch the sick animals
TARGET_SPECIFICITY = 0.70  # 70% - acceptable false positive rate

# CORS settings
CORS_ORIGINS = ['*']  # Allow all origins for development

# Debug mode
DEBUG = os.environ.get('FLASK_ENV') != 'production'
