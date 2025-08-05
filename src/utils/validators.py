"""
Input validation utilities for the Fal Gram Bot.
"""

import re
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

class Validator:
    """Input validation class."""
    
    @staticmethod
    def validate_name(name: str) -> tuple[bool, str]:
        """Validate user name."""
        if not name or not name.strip():
            return False, "Name cannot be empty"
        
        name = name.strip()
        
        if len(name) < 2:
            return False, "Name must be at least 2 characters long"
        
        if len(name) > 50:
            return False, "Name must be less than 50 characters"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not re.match(r'^[a-zA-ZÀ-ÿ\s\'-]+$', name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, "Valid name"
    
    @staticmethod
    def validate_birth_date(birth_date_str: str) -> tuple[bool, str]:
        """Validate birth date string."""
        try:
            # Try different date formats
            formats = ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y", "%m-%d-%Y"]
            birth_date = None
            
            for fmt in formats:
                try:
                    birth_date = datetime.strptime(birth_date_str, fmt)
                    break
                except ValueError:
                    continue
            
            if not birth_date:
                return False, "Invalid date format. Please use YYYY-MM-DD"
            
            # Check if date is in the future
            if birth_date > datetime.now():
                return False, "Birth date cannot be in the future"
            
            # Check if age is reasonable (0-120 years)
            age = datetime.now().year - birth_date.year
            if age < 0 or age > 120:
                return False, "Age must be between 0 and 120 years"
            
            return True, "Valid birth date"
            
        except Exception:
            return False, "Invalid date format"
    
    @staticmethod
    def validate_email(email: str) -> tuple[bool, str]:
        """Validate email address."""
        if not email or not email.strip():
            return False, "Email cannot be empty"
        
        email = email.strip().lower()
        
        # Basic email pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        # Check for common invalid domains
        invalid_domains = ['example.com', 'test.com', 'localhost']
        domain = email.split('@')[1]
        if domain in invalid_domains:
            return False, "Please use a valid email address"
        
        return True, "Valid email"
    
    @staticmethod
    def validate_phone(phone: str) -> tuple[bool, str]:
        """Validate phone number."""
        if not phone or not phone.strip():
            return False, "Phone number cannot be empty"
        
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check length
        if len(digits_only) < 7:
            return False, "Phone number must be at least 7 digits"
        
        if len(digits_only) > 15:
            return False, "Phone number must be less than 15 digits"
        
        return True, "Valid phone number"
    
    @staticmethod
    def validate_text(text: str, max_length: int = 1000, min_length: int = 1) -> tuple[bool, str]:
        """Validate text input."""
        if not text or not text.strip():
            return False, "Text cannot be empty"
        
        text = text.strip()
        
        if len(text) < min_length:
            return False, f"Text must be at least {min_length} characters long"
        
        if len(text) > max_length:
            return False, f"Text must be less than {max_length} characters"
        
        # Check for excessive whitespace
        if re.search(r'\s{3,}', text):
            return False, "Text contains excessive whitespace"
        
        return True, "Valid text"
    
    @staticmethod
    def validate_choice(choice: str, valid_choices: List[str]) -> tuple[bool, str]:
        """Validate choice from a list of valid options."""
        if not choice or not choice.strip():
            return False, "Please select a valid option"
        
        choice = choice.strip()
        
        if choice not in valid_choices:
            return False, f"Please select from: {', '.join(valid_choices)}"
        
        return True, "Valid choice"
    
    @staticmethod
    def validate_numeric(value: str, min_value: Optional[float] = None, 
                        max_value: Optional[float] = None) -> tuple[bool, str]:
        """Validate numeric input."""
        if not value or not value.strip():
            return False, "Value cannot be empty"
        
        try:
            num_value = float(value)
        except ValueError:
            return False, "Value must be a number"
        
        if min_value is not None and num_value < min_value:
            return False, f"Value must be at least {min_value}"
        
        if max_value is not None and num_value > max_value:
            return False, f"Value must be at most {max_value}"
        
        return True, "Valid number"
    
    @staticmethod
    def validate_username(username: str) -> tuple[bool, str]:
        """Validate username."""
        if not username or not username.strip():
            return False, "Username cannot be empty"
        
        username = username.strip()
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long"
        
        if len(username) > 30:
            return False, "Username must be less than 30 characters"
        
        # Check for valid characters (letters, numbers, underscores)
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        # Check if starts with letter
        if not username[0].isalpha():
            return False, "Username must start with a letter"
        
        return True, "Valid username"
    
    @staticmethod
    def sanitize_input(text: str, max_length: int = 1000) -> str:
        """Sanitize user input."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text
    
    @staticmethod
    def validate_json(json_str: str) -> tuple[bool, str]:
        """Validate JSON string."""
        if not json_str or not json_str.strip():
            return False, "JSON string cannot be empty"
        
        try:
            import json
            json.loads(json_str)
            return True, "Valid JSON"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {str(e)}"

# Global validator instance
validator = Validator()