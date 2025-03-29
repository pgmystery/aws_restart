import json
import urllib
from datetime import datetime


def get_public_ip():
    try:
        # Make a request to a public IP service (ipify)
        with urllib.request.urlopen('https://api.ipify.org?format=json') as response:
            # Read the response and decode it to a string
            data = response.read().decode()
            # Parse the JSON response
            ip_info = json.loads(data)
            # Return the public IP
            return ip_info['ip']
    except urllib.error.URLError as e:
        print(f"Error: {e}")
        return None


def datetime_converter(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()  # Convert datetime to ISO format string
    raise TypeError(f"Type {type(obj)} not serializable")
