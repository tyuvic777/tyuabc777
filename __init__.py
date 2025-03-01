# Initialize the Flask frontend application
from .app import app  # Import the Flask app from app.py

# Add any package-wide configurations or imports
__all__ = ['app']  # Expose app for imports