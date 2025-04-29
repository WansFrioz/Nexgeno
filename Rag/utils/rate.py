import json
import os
from datetime import datetime


RATE_LIMIT_FILE = "rate_limits.json"
DAILY_LIMIT = 12

def load_rate_limits():
    if os.path.exists(RATE_LIMIT_FILE):
        try:
            with open(RATE_LIMIT_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # If file is empty or invalid, return fresh dict
            return {}
    return {}

def save_rate_limits(data):
    with open(RATE_LIMIT_FILE, "w") as f:
        json.dump(data, f)

def is_user_rate_limited(user_id):
    rate_limits = load_rate_limits()
    today = datetime.utcnow().date().isoformat()

    # Initialize or reset counter for a new day
    if user_id not in rate_limits or rate_limits[user_id]["date"] != today:
        rate_limits[user_id] = {"count": 0, "date": today}
    
    # Check if user exceeded the limit
    if rate_limits[user_id]["count"] >= DAILY_LIMIT:
        return True

    # Increment count and save
    rate_limits[user_id]["count"] += 1
    save_rate_limits(rate_limits)
    return False