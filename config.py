"""
Configuration settings for the backend
"""
import os
from dotenv import load_dotenv

# Load .env file with error handling for encoding issues
try:
    load_dotenv()
except Exception as e:
    # If .env file has encoding issues, continue with defaults
    print(f"Warning: Could not load .env file: {e}")
    print("Continuing with default configuration...")

# Database Configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///reviews.db')

# LLM Configuration
USE_GEMINI = os.getenv('USE_GEMINI', 'true').lower() == 'true'
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', '')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# API Configuration
API_HOST = os.getenv('API_HOST', '0.0.0.0')
API_PORT = int(os.getenv('API_PORT', 5000))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')

# Application Configuration
DEBUG = os.getenv('DEBUG', 'false').lower() == 'true'
MAX_REVIEW_LENGTH = 5000
MIN_REVIEW_LENGTH = 1

