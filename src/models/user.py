"""
User model for the Fal Gram Bot.
Contains data structures for user information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class User:
    """User data model."""
    
    user_id: int
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language: str = "en"
    is_premium: bool = False
    premium_plan: Optional[str] = None
    premium_expires_at: Optional[datetime] = None
    premium_purchased_at: Optional[datetime] = None
    premium_cancelled_at: Optional[datetime] = None
    premium_gifted_at: Optional[datetime] = None
    daily_readings_used: int = 0
    total_readings: int = 0
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    referral_earnings: int = 0
    referral_count: int = 0
    daily_card_subscribed: bool = False
    daily_card_time: str = "09:00"
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary."""
        return {
            "user_id": self.user_id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "language": self.language,
            "is_premium": self.is_premium,
            "premium_plan": self.premium_plan,
            "premium_expires_at": self.premium_expires_at.isoformat() if self.premium_expires_at else None,
            "premium_purchased_at": self.premium_purchased_at.isoformat() if self.premium_purchased_at else None,
            "premium_cancelled_at": self.premium_cancelled_at.isoformat() if self.premium_cancelled_at else None,
            "premium_gifted_at": self.premium_gifted_at.isoformat() if self.premium_gifted_at else None,
            "daily_readings_used": self.daily_readings_used,
            "total_readings": self.total_readings,
            "referral_code": self.referral_code,
            "referred_by": self.referred_by,
            "referral_earnings": self.referral_earnings,
            "referral_count": self.referral_count,
            "daily_card_subscribed": self.daily_card_subscribed,
            "daily_card_time": self.daily_card_time,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "last_activity": self.last_activity.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create user from dictionary."""
        # Parse datetime fields
        premium_expires_at = None
        if data.get('premium_expires_at'):
            try:
                premium_expires_at = datetime.fromisoformat(data['premium_expires_at'])
            except ValueError:
                pass
        
        premium_purchased_at = None
        if data.get('premium_purchased_at'):
            try:
                premium_purchased_at = datetime.fromisoformat(data['premium_purchased_at'])
            except ValueError:
                pass
        
        premium_cancelled_at = None
        if data.get('premium_cancelled_at'):
            try:
                premium_cancelled_at = datetime.fromisoformat(data['premium_cancelled_at'])
            except ValueError:
                pass
        
        premium_gifted_at = None
        if data.get('premium_gifted_at'):
            try:
                premium_gifted_at = datetime.fromisoformat(data['premium_gifted_at'])
            except ValueError:
                pass
        
        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        updated_at = datetime.now()
        if data.get('updated_at'):
            try:
                updated_at = datetime.fromisoformat(data['updated_at'])
            except ValueError:
                pass
        
        last_activity = datetime.now()
        if data.get('last_activity'):
            try:
                last_activity = datetime.fromisoformat(data['last_activity'])
            except ValueError:
                pass
        
        return cls(
            user_id=data['user_id'],
            first_name=data['first_name'],
            last_name=data.get('last_name'),
            username=data.get('username'),
            language=data.get('language', 'en'),
            is_premium=data.get('is_premium', False),
            premium_plan=data.get('premium_plan'),
            premium_expires_at=premium_expires_at,
            premium_purchased_at=premium_purchased_at,
            premium_cancelled_at=premium_cancelled_at,
            premium_gifted_at=premium_gifted_at,
            daily_readings_used=data.get('daily_readings_used', 0),
            total_readings=data.get('total_readings', 0),
            referral_code=data.get('referral_code'),
            referred_by=data.get('referred_by'),
            referral_earnings=data.get('referral_earnings', 0),
            referral_count=data.get('referral_count', 0),
            daily_card_subscribed=data.get('daily_card_subscribed', False),
            daily_card_time=data.get('daily_card_time', '09:00'),
            created_at=created_at,
            updated_at=updated_at,
            last_activity=last_activity
        )
    
    def is_premium_active(self) -> bool:
        """Check if premium subscription is active."""
        if not self.is_premium:
            return False
        
        if not self.premium_expires_at:
            return False
        
        return datetime.now() < self.premium_expires_at
    
    def can_use_free_reading(self) -> bool:
        """Check if user can use a free reading."""
        from config.settings import settings
        
        if self.is_premium_active():
            return True
        
        return self.daily_readings_used < settings.FREE_DAILY_LIMIT
    
    def get_full_name(self) -> str:
        """Get user's full name."""
        if self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name
    
    def get_display_name(self) -> str:
        """Get user's display name (username or full name)."""
        if self.username:
            return f"@{self.username}"
        return self.get_full_name() 