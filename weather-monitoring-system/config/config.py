import os

API_KEY = os.getenv('OPENWEATHERMAP_API_KEY', 'your_default_api_key')
INTERVAL = int(os.getenv('INTERVAL', 300))  # Default interval: 5 minutes
