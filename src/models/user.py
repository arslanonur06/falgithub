"""
User model for the Fal Gram Bot.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class User:
    """User model class."""
    
    # Basic user info
    user_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    language_code: str = "en"
    
    # Profile info
    birth_date: Optional[datetime] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    
    # Bot settings
    is_premium: bool = False
    is_admin: bool = False
    is_blocked: bool = False
    
    # Usage tracking
    daily_usage_count: int = 0
    total_usage_count: int = 0
    last_usage_date: Optional[datetime] = None
    
    # Referral system
    referral_code: Optional[str] = None
    referred_by: Optional[int] = None
    referral_count: int = 0
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    last_activity: datetime = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.last_activity is None:
            self.last_activity = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        user_dict = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in user_dict.items():
            if isinstance(value, datetime):
                user_dict[key] = value.isoformat()
        
        return user_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        # Convert ISO format strings back to datetime objects
        for key in ['birth_date', 'created_at', 'updated_at', 'last_activity', 'last_usage_date']:
            if key in data and data[key]:
                try:
                    data[key] = datetime.fromisoformat(data[key])
                except (ValueError, TypeError):
                    data[key] = None
        
        return cls(**data)
    
    def update_activity(self) -> None:
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
        self.updated_at = datetime.now()
    
    def increment_usage(self) -> None:
        """Increment usage counters."""
        today = datetime.now().date()
        
        # Reset daily usage if it's a new day
        if self.last_usage_date and self.last_usage_date.date() != today:
            self.daily_usage_count = 0
        
        self.daily_usage_count += 1
        self.total_usage_count += 1
        self.last_usage_date = datetime.now()
        self.update_activity()
    
    def can_use_service(self) -> bool:
        """Check if user can use the service (not blocked and within limits)."""
        if self.is_blocked:
            return False
        
        if self.is_premium:
            return True
        
        # Check daily limit for free users
        return self.daily_usage_count < 3  # Free daily limit
    
    def get_remaining_uses(self) -> int:
        """Get remaining uses for today."""
        if self.is_premium:
            return float('inf')  # Unlimited for premium users
        
        return max(0, 3 - self.daily_usage_count)  # 3 free uses per day
    
    def get_full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return f"@{self.username}"
        else:
            return f"User {self.user_id}"
    
    def is_new_user(self) -> bool:
        """Check if user is new (created within last 24 hours)."""
        if not self.created_at:
            return True
        
        return (datetime.now() - self.created_at).days < 1