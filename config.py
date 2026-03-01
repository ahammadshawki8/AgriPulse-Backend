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

# Temperature ranges (Celsius)
NORMAL_TEMP_RANGES = {
    'head': (37.5, 38.5),
    'udder': (37.5, 38.5),
    'leg': (37.0, 38.0),
    'hoof': (37.0, 38.0),
    'body': (37.5, 38.5),
    'neck': (37.5, 38.5),
    'tail': (37.0, 38.0)
}

# CORS settings
CORS_ORIGINS = ['*']  # Allow all origins for development

# Debug mode
DEBUG = True
