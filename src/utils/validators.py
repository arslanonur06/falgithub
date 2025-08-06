"""
Input validation utilities for the Fal Gram Bot.
Contains functions to validate various types of input data.
"""

import re
from typing import Dict, Any, Optional
from datetime import datetime


def validate_user_input(text: str, max_length: int = 1000) -> bool:
    """
    Validate user input text.
    
    Args:
        text: Text to validate
        max_length: Maximum allowed length
    
    Returns:
        True if valid, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    
    if len(text.strip()) == 0:
        return False
    
    if len(text) > max_length:
        return False
    
    # Check for potentially dangerous content
    dangerous_patterns = [
        r'<script',
        r'javascript:',
        r'data:text/html',
        r'vbscript:',
        r'onload=',
        r'onerror='
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    
    return True


def validate_birth_date_format(text: str) -> bool:
    """
    Validate birth date format (DD.MM.YYYY HH:MM - City).
    
    Args:
        text: Birth date text to validate
    
    Returns:
        True if valid format, False otherwise
    """
    if not text or not isinstance(text, str):
        return False
    
    # Expected format: DD.MM.YYYY HH:MM - City
    pattern = r'^\d{2}\.\d{2}\.\d{4}\s+\d{2}:\d{2}\s+-\s+.+$'
    
    if not re.match(pattern, text):
        return False
    
    try:
        # Extract date part and validate
        date_part = text.split(' - ')[0]
        datetime.strptime(date_part, "%d.%m.%Y %H:%M")
        return True
    except ValueError:
        return False


def validate_zodiac_sign(sign: str) -> bool:
    """
    Validate zodiac sign.
    
    Args:
        sign: Zodiac sign to validate
    
    Returns:
        True if valid, False otherwise
    """
    valid_signs = [
        'aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo',
        'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces'
    ]
    
    return sign.lower() in valid_signs


def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format.
    
    Args:
        phone: Phone number to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid length (7-15 digits)
    return 7 <= len(digits_only) <= 15


def validate_email(email: str) -> bool:
    """
    Validate email format.
    
    Args:
        email: Email to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_user_id(user_id: Any) -> bool:
    """
    Validate user ID.
    
    Args:
        user_id: User ID to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        user_id_int = int(user_id)
        return user_id_int > 0
    except (ValueError, TypeError):
        return False


def validate_premium_plan(plan: str) -> bool:
    """
    Validate premium plan name.
    
    Args:
        plan: Plan name to validate
    
    Returns:
        True if valid, False otherwise
    """
    valid_plans = ['basic', 'premium', 'vip']
    return plan.lower() in valid_plans


def validate_language_code(lang: str) -> bool:
    """
    Validate language code.
    
    Args:
        lang: Language code to validate
    
    Returns:
        True if valid, False otherwise
    """
    valid_languages = ['en', 'tr', 'es']
    return lang.lower() in valid_languages


def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize text for safe storage/display.
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized text
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Remove potentially dangerous characters
    text = re.sub(r'[<>"\']', '', text)
    
    # Remove extra whitespace
    text = ' '.join(text.split())
    
    # Limit length
    if len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_payment_amount(amount: Any) -> bool:
    """
    Validate payment amount.
    
    Args:
        amount: Amount to validate
    
    Returns:
        True if valid, False otherwise
    """
    try:
        amount_float = float(amount)
        return amount_float > 0 and amount_float <= 10000  # Max 10,000
    except (ValueError, TypeError):
        return False


def validate_referral_code(code: str) -> bool:
    """
    Validate referral code format.
    
    Args:
        code: Referral code to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not code or not isinstance(code, str):
        return False
    
    # Check if it's alphanumeric and 8 characters long
    pattern = r'^[A-Z0-9]{8}$'
    return re.match(pattern, code) is not None 