"""
Tests for utility functions.
"""

import pytest
from datetime import datetime
from src.utils.helpers import (
    generate_referral_code,
    validate_email,
    validate_phone,
    sanitize_text,
    format_currency,
    calculate_age,
    is_valid_birth_date,
    chunk_list,
    safe_get
)
from src.utils.validators import Validator

class TestHelpers:
    """Test helper functions."""
    
    def test_generate_referral_code(self):
        """Test referral code generation."""
        user_id = 12345
        code = generate_referral_code(user_id)
        
        assert len(code) == 8
        assert code.isalnum()
        assert code.isupper()
    
    def test_validate_email(self):
        """Test email validation."""
        # Valid emails
        assert validate_email("test@example.com") == True
        assert validate_email("user.name@domain.co.uk") == True
        assert validate_email("test+tag@example.com") == True
        
        # Invalid emails
        assert validate_email("") == False
        assert validate_email("invalid-email") == False
        assert validate_email("@example.com") == False
        assert validate_email("test@") == False
    
    def test_validate_phone(self):
        """Test phone validation."""
        # Valid phones
        assert validate_phone("1234567890") == True
        assert validate_phone("+1-234-567-8900") == True
        assert validate_phone("(123) 456-7890") == True
        
        # Invalid phones
        assert validate_phone("") == False
        assert validate_phone("123") == False  # Too short
        assert validate_phone("12345678901234567890") == False  # Too long
    
    def test_sanitize_text(self):
        """Test text sanitization."""
        # Normal text
        assert sanitize_text("Hello World") == "Hello World"
        
        # Text with excessive whitespace
        assert sanitize_text("  Hello   World  ") == "Hello World"
        
        # Text too long
        long_text = "A" * 1001
        sanitized = sanitize_text(long_text)
        assert len(sanitized) <= 1003  # max_length + "..."
        assert sanitized.endswith("...")
        
        # Empty text
        assert sanitize_text("") == ""
        assert sanitize_text(None) == ""
    
    def test_format_currency(self):
        """Test currency formatting."""
        assert format_currency(100.50) == "$100.50"
        assert format_currency(0) == "$0.00"
        assert format_currency(100.50, "EUR") == "€100.50"
        assert format_currency(100.50, "TRY") == "₺100.50"
    
    def test_calculate_age(self):
        """Test age calculation."""
        # Test with current date
        today = datetime.now()
        birth_date = datetime(today.year - 25, today.month, today.day)
        assert calculate_age(birth_date) == 25
        
        # Test with future date
        future_date = datetime(today.year + 1, today.month, today.day)
        assert calculate_age(future_date) == -1
    
    def test_is_valid_birth_date(self):
        """Test birth date validation."""
        today = datetime.now()
        
        # Valid birth dates
        valid_date = datetime(today.year - 25, today.month, today.day)
        assert is_valid_birth_date(valid_date) == True
        
        # Invalid birth dates
        future_date = datetime(today.year + 1, today.month, today.day)
        assert is_valid_birth_date(future_date) == False
        
        # Too old (over 120 years)
        old_date = datetime(today.year - 121, today.month, today.day)
        assert is_valid_birth_date(old_date) == False
    
    def test_chunk_list(self):
        """Test list chunking."""
        test_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        
        # Test chunking by 3
        chunks = chunk_list(test_list, 3)
        assert len(chunks) == 4
        assert chunks[0] == [1, 2, 3]
        assert chunks[1] == [4, 5, 6]
        assert chunks[2] == [7, 8, 9]
        assert chunks[3] == [10]
        
        # Test chunking by 5
        chunks = chunk_list(test_list, 5)
        assert len(chunks) == 2
        assert chunks[0] == [1, 2, 3, 4, 5]
        assert chunks[1] == [6, 7, 8, 9, 10]
    
    def test_safe_get(self):
        """Test safe dictionary access."""
        test_dict = {
            "level1": {
                "level2": {
                    "level3": "value"
                }
            }
        }
        
        # Test successful access
        assert safe_get(test_dict, "level1.level2.level3") == "value"
        assert safe_get(test_dict, "level1.level2") == {"level3": "value"}
        
        # Test with default value
        assert safe_get(test_dict, "nonexistent", "default") == "default"
        assert safe_get(test_dict, "level1.nonexistent", "default") == "default"

class TestValidators:
    """Test validator functions."""
    
    def test_validate_name(self):
        """Test name validation."""
        validator = Validator()
        
        # Valid names
        assert validator.validate_name("John")[0] == True
        assert validator.validate_name("Mary Jane")[0] == True
        assert validator.validate_name("Jean-Pierre")[0] == True
        
        # Invalid names
        assert validator.validate_name("")[0] == False
        assert validator.validate_name("A")[0] == False  # Too short
        assert validator.validate_name("A" * 51)[0] == False  # Too long
        assert validator.validate_name("John123")[0] == False  # Contains numbers
    
    def test_validate_text(self):
        """Test text validation."""
        validator = Validator()
        
        # Valid text
        assert validator.validate_text("Hello World")[0] == True
        assert validator.validate_text("A")[0] == True  # Minimum length
        
        # Invalid text
        assert validator.validate_text("")[0] == False
        assert validator.validate_text("A" * 1001)[0] == False  # Too long
        assert validator.validate_text("Hello   World")[0] == False  # Excessive whitespace
    
    def test_validate_numeric(self):
        """Test numeric validation."""
        validator = Validator()
        
        # Valid numbers
        assert validator.validate_numeric("123")[0] == True
        assert validator.validate_numeric("123.45")[0] == True
        assert validator.validate_numeric("0")[0] == True
        
        # Invalid numbers
        assert validator.validate_numeric("")[0] == False
        assert validator.validate_numeric("abc")[0] == False
        assert validator.validate_numeric("12.34.56")[0] == False
        
        # Test with min/max values
        assert validator.validate_numeric("5", min_value=1, max_value=10)[0] == True
        assert validator.validate_numeric("0", min_value=1)[0] == False
        assert validator.validate_numeric("15", max_value=10)[0] == False