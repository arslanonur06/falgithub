"""
Helper utility functions for the Fal Gram Bot.
"""

import re
import hashlib
import random
import string
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

def generate_referral_code(user_id: int, length: int = 8) -> str:
    """Generate a unique referral code for a user."""
    # Create a hash from user_id and timestamp
    timestamp = str(datetime.now().timestamp())
    hash_input = f"{user_id}{timestamp}"
    hash_value = hashlib.md5(hash_input.encode()).hexdigest()
    
    # Take first part of hash and convert to uppercase
    code = hash_value[:length].upper()
    
    # Ensure it's alphanumeric
    code = re.sub(r'[^A-Z0-9]', '', code)
    
    # If too short, pad with random characters
    while len(code) < length:
        code += random.choice(string.ascii_uppercase + string.digits)
    
    return code[:length]

def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """Sanitize user input text."""
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def format_currency(amount: float, currency: str = "USD") -> str:
    """Format currency amount."""
    currency_symbols = {
        "USD": "$",
        "EUR": "€",
        "TRY": "₺",
        "GBP": "£"
    }
    
    symbol = currency_symbols.get(currency, currency)
    return f"{symbol}{amount:.2f}"

def format_date(date: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime object."""
    return date.strftime(format_str)

def parse_date(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """Parse date string to datetime object."""
    try:
        return datetime.strptime(date_str, format_str)
    except ValueError:
        return None

def calculate_age(birth_date: datetime) -> int:
    """Calculate age from birth date."""
    today = datetime.now()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    return age

def is_valid_birth_date(birth_date: datetime) -> bool:
    """Check if birth date is valid (not in future, reasonable age)."""
    today = datetime.now()
    
    # Check if date is in the future
    if birth_date > today:
        return False
    
    # Check if age is reasonable (0-120 years)
    age = calculate_age(birth_date)
    return 0 <= age <= 120

def chunk_list(lst: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size."""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_dict(d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
    """Flatten a nested dictionary."""
    items = []
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def safe_get(dictionary: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get a value from a dictionary."""
    keys = key.split('.')
    value = dictionary
    
    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            return default
    
    return value

def generate_random_string(length: int = 10) -> str:
    """Generate a random string of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def is_weekend(date: datetime) -> bool:
    """Check if a date falls on a weekend."""
    return date.weekday() >= 5

def get_next_weekday(date: datetime) -> datetime:
    """Get the next weekday from a given date."""
    next_day = date + timedelta(days=1)
    while is_weekend(next_day):
        next_day += timedelta(days=1)
    return next_day

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string."""
    if seconds < 60:
        return f"{seconds} seconds"
    elif seconds < 3600:
        minutes = seconds // 60
        return f"{minutes} minutes"
    elif seconds < 86400:
        hours = seconds // 3600
        return f"{hours} hours"
    else:
        days = seconds // 86400
        return f"{days} days"

def calculate_moon_phase(date=None):
    """Calculate moon phase for a given date."""
    if date is None:
        date = datetime.now()
    
    # Known new moon date (January 6, 2000)
    known_new_moon = datetime(2000, 1, 6, 18, 14, 0)
    
    # Calculate days since known new moon
    days_since = (date - known_new_moon).days
    
    # Moon cycle is approximately 29.530588853 days
    moon_cycle = 29.530588853
    phase = (days_since % moon_cycle) / moon_cycle
    
    # Calculate illumination percentage
    if phase <= 0.5:
        illumination = phase * 2
    else:
        illumination = (1 - phase) * 2
    
    # Determine moon phase name
    if phase < 0.0625:
        phase_name = "New Moon"
    elif phase < 0.1875:
        phase_name = "Waxing Crescent"
    elif phase < 0.3125:
        phase_name = "First Quarter"
    elif phase < 0.4375:
        phase_name = "Waxing Gibbous"
    elif phase < 0.5625:
        phase_name = "Full Moon"
    elif phase < 0.6875:
        phase_name = "Waning Gibbous"
    elif phase < 0.8125:
        phase_name = "Last Quarter"
    elif phase < 0.9375:
        phase_name = "Waning Crescent"
    else:
        phase_name = "New Moon"
    
    return {
        'phase': phase_name,
        'illumination': round(illumination * 100, 1),
        'phase_value': phase,
        'days_since_new': days_since % moon_cycle
    }