import json
from datetime import datetime

# Utility function for JSON printing
def pretty_print(data):
    print(json.dumps(data, indent=2))

# Utility function to get current timestamp
def get_timestamp():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
