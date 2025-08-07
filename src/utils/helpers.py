"""
Helper functions for the Fal Gram Bot.
Contains various utility functions used throughout the application.
"""

import re
from datetime import datetime, timedelta, date as date_cls
from typing import Dict, Any, Optional, Union


def format_currency(amount: float, currency: str = "TRY") -> str:
    """Format currency amount."""
    return f"{amount:.2f} {currency}"


def format_date(date: datetime) -> str:
    """Format date for display."""
    return date.strftime("%d.%m.%Y %H:%M")


def calculate_moon_phase(date: datetime = None) -> Dict[str, Any]:
    """
    Calculate moon phase for a given date.
    
    Args:
        date: Date to calculate moon phase for (defaults to current date)
    
    Returns:
        Dictionary with moon phase information
    """
    if not date:
        date = datetime.now()
    
    # Simple moon phase calculation (approximate)
    # This is a simplified version - for more accuracy, use astronomical libraries
    
    # Moon phases cycle every ~29.5 days
    # Starting from a known new moon date
    known_new_moon = datetime(2024, 1, 11)  # Known new moon date
    days_since_new_moon = (date - known_new_moon).days
    
    # Calculate phase (0-1, where 0 is new moon, 0.5 is full moon)
    phase = (days_since_new_moon % 29.5) / 29.5
    
    # Determine moon phase name
    if phase < 0.0625:
        phase_name = "New Moon"
        phase_emoji = "🌑"
    elif phase < 0.1875:
        phase_name = "Waxing Crescent"
        phase_emoji = "🌒"
    elif phase < 0.3125:
        phase_name = "First Quarter"
        phase_emoji = "🌓"
    elif phase < 0.4375:
        phase_name = "Waxing Gibbous"
        phase_emoji = "🌔"
    elif phase < 0.5625:
        phase_name = "Full Moon"
        phase_emoji = "🌕"
    elif phase < 0.6875:
        phase_name = "Waning Gibbous"
        phase_emoji = "🌖"
    elif phase < 0.8125:
        phase_name = "Last Quarter"
        phase_emoji = "🌗"
    elif phase < 0.9375:
        phase_name = "Waning Crescent"
        phase_emoji = "🌘"
    else:
        phase_name = "New Moon"
        phase_emoji = "🌑"
    
    return {
        "phase": phase_name,
        "emoji": phase_emoji,
        "percentage": int(phase * 100),
        "date": date.strftime("%d.%m.%Y")
    }


def validate_phone_number(phone: str) -> bool:
    """Validate phone number format."""
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def sanitize_text(text: str) -> str:
    """Sanitize text for safe storage/display."""
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    # Limit length
    return text[:1000] if len(text) > 1000 else text


def generate_referral_code(user_id: int) -> str:
    """Generate a referral code for a user."""
    import hashlib
    # Create a hash from user_id and timestamp
    data = f"{user_id}_{datetime.now().timestamp()}"
    hash_object = hashlib.md5(data.encode())
    # Take first 8 characters of hex digest
    return hash_object.hexdigest()[:8].upper()


def parse_birth_info(birth_text: str) -> Optional[Dict[str, Any]]:
    """
    Parse birth information from text.
    
    Expected format: DD.MM.YYYY HH:MM - City
    
    Args:
        birth_text: Birth information text
    
    Returns:
        Dictionary with parsed birth info or None if invalid
    """
    try:
        # Remove extra spaces and split by dash
        parts = birth_text.strip().split('-')
        if len(parts) != 2:
            return None
        
        date_time_part = parts[0].strip()
        city = parts[1].strip()
        
        # Parse date and time
        date_time = datetime.strptime(date_time_part, "%d.%m.%Y %H:%M")
        
        return {
            "date": date_time,
            "city": city,
            "formatted": date_time.strftime("%d.%m.%Y %H:%M")
        }
    except Exception:
        return None


def get_zodiac_sign(birth_date: datetime) -> str:
    """Get zodiac sign based on birth date."""
    month = birth_date.month
    day = birth_date.day
    
    if (month == 3 and day >= 21) or (month == 4 and day <= 19):
        return "aries"
    elif (month == 4 and day >= 20) or (month == 5 and day <= 20):
        return "taurus"
    elif (month == 5 and day >= 21) or (month == 6 and day <= 20):
        return "gemini"
    elif (month == 6 and day >= 21) or (month == 7 and day <= 22):
        return "cancer"
    elif (month == 7 and day >= 23) or (month == 8 and day <= 22):
        return "leo"
    elif (month == 8 and day >= 23) or (month == 9 and day <= 22):
        return "virgo"
    elif (month == 9 and day >= 23) or (month == 10 and day <= 22):
        return "libra"
    elif (month == 10 and day >= 23) or (month == 11 and day <= 21):
        return "scorpio"
    elif (month == 11 and day >= 22) or (month == 12 and day <= 21):
        return "sagittarius"
    elif (month == 12 and day >= 22) or (month == 1 and day <= 19):
        return "capricorn"
    elif (month == 1 and day >= 20) or (month == 2 and day <= 18):
        return "aquarius"
    else:
        return "pisces"


def format_time_duration(seconds: int) -> str:
    """Format time duration in a human-readable format."""
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


# === Added for astrology helpers ===
def _parse_birth_date(value: Union[str, datetime, date_cls]) -> Optional[datetime]:
    """Parse various birth date formats to a datetime.
    Accepts ISO strings (YYYY-MM-DD or YYYY-MM-DDTHH:MM[:SS]),
    'DD.MM.YYYY' with optional ' HH:MM', or datetime/date objects.
    """
    if isinstance(value, datetime):
        return value
    if isinstance(value, date_cls):
        return datetime.combine(value, datetime.min.time())
    if not isinstance(value, str):
        return None

    text = value.strip()
    # Try ISO format first
    try:
        return datetime.fromisoformat(text)
    except Exception:
        pass

    # Try DD.MM.YYYY HH:MM
    for fmt in ("%d.%m.%Y %H:%M", "%d.%m.%Y"):
        try:
            return datetime.strptime(text, fmt)
        except Exception:
            continue
    return None


def is_valid_birth_date(value: Union[str, datetime, date_cls]) -> bool:
    """Validate birth date is a real date, not in the future, and age in [0, 120]."""
    dt = _parse_birth_date(value)
    if dt is None:
        return False
    now = datetime.now()
    if dt > now:
        return False
    years = calculate_age(dt)
    return 0 <= years <= 120


def calculate_age(birth_date: Union[str, datetime, date_cls]) -> int:
    """Calculate age in whole years from a birth date.

    Args:
        birth_date: Birth date as str, datetime, or date.
    Returns:
        Age in years (int). Returns 0 if parsing fails.
    """
    dt = _parse_birth_date(birth_date)
    if dt is None:
        return 0
    today = datetime.today().date()
    bdate = dt.date()
    years = today.year - bdate.year - ((today.month, today.day) < (bdate.month, bdate.day))
    return max(0, years)