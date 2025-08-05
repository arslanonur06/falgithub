"""
Payment model for the Fal Gram Bot.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class Payment:
    """Payment model class."""
    
    # Payment identification
    payment_id: str
    user_id: int
    
    # Payment details
    amount: float
    currency: str = "TRY"
    plan_name: str = "premium"
    
    # Payment status
    status: str = "pending"  # pending, completed, failed, refunded, cancelled
    
    # Payment provider info
    provider: str = "telegram"  # telegram, stripe, etc.
    provider_payment_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert payment to dictionary."""
        payment_dict = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in payment_dict.items():
            if isinstance(value, datetime):
                payment_dict[key] = value.isoformat()
        
        return payment_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create payment from dictionary."""
        # Convert ISO format strings back to datetime objects
        for key in ['created_at', 'completed_at', 'updated_at']:
            if key in data and data[key]:
                try:
                    data[key] = datetime.fromisoformat(data[key])
                except (ValueError, TypeError):
                    data[key] = None
        
        return cls(**data)
    
    def mark_completed(self, provider_payment_id: Optional[str] = None) -> None:
        """Mark payment as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
        
        if provider_payment_id:
            self.provider_payment_id = provider_payment_id
    
    def mark_failed(self) -> None:
        """Mark payment as failed."""
        self.status = "failed"
        self.updated_at = datetime.now()
    
    def mark_refunded(self) -> None:
        """Mark payment as refunded."""
        self.status = "refunded"
        self.updated_at = datetime.now()
    
    def mark_cancelled(self) -> None:
        """Mark payment as cancelled."""
        self.status = "cancelled"
        self.updated_at = datetime.now()
    
    def is_completed(self) -> bool:
        """Check if payment is completed."""
        return self.status == "completed"
    
    def is_pending(self) -> bool:
        """Check if payment is pending."""
        return self.status == "pending"
    
    def is_failed(self) -> bool:
        """Check if payment is failed."""
        return self.status == "failed"
    
    def is_refunded(self) -> bool:
        """Check if payment is refunded."""
        return self.status == "refunded"
    
    def is_cancelled(self) -> bool:
        """Check if payment is cancelled."""
        return self.status == "cancelled"
    
    def get_formatted_amount(self) -> str:
        """Get formatted amount with currency."""
        return f"{self.amount:.2f} {self.currency}"
    
    def get_duration_days(self) -> int:
        """Get subscription duration in days based on plan."""
        plan_durations = {
            "basic": 30,
            "premium": 30,
            "vip": 30
        }
        return plan_durations.get(self.plan_name, 30)

@dataclass
class Subscription:
    """Subscription model class."""
    
    # Subscription identification
    subscription_id: str
    user_id: int
    
    # Subscription details
    plan_name: str = "premium"
    status: str = "active"  # active, cancelled, expired, suspended
    
    # Duration
    start_date: datetime = None
    end_date: datetime = None
    
    # Payment info
    payment_id: Optional[str] = None
    auto_renew: bool = False
    
    # Timestamps
    created_at: datetime = None
    cancelled_at: Optional[datetime] = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.start_date is None:
            self.start_date = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary."""
        subscription_dict = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in subscription_dict.items():
            if isinstance(value, datetime):
                subscription_dict[key] = value.isoformat()
        
        return subscription_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """Create subscription from dictionary."""
        # Convert ISO format strings back to datetime objects
        for key in ['start_date', 'end_date', 'created_at', 'cancelled_at', 'updated_at']:
            if key in data and data[key]:
                try:
                    data[key] = datetime.fromisoformat(data[key])
                except (ValueError, TypeError):
                    data[key] = None
        
        return cls(**data)
    
    def cancel(self) -> None:
        """Cancel subscription."""
        self.status = "cancelled"
        self.cancelled_at = datetime.now()
        self.updated_at = datetime.now()
    
    def suspend(self) -> None:
        """Suspend subscription."""
        self.status = "suspended"
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """Activate subscription."""
        self.status = "active"
        self.updated_at = datetime.now()
    
    def extend(self, days: int) -> None:
        """Extend subscription by specified days."""
        if self.end_date:
            self.end_date = self.end_date + timedelta(days=days)
        else:
            self.end_date = datetime.now() + timedelta(days=days)
        
        self.updated_at = datetime.now()
    
    def is_active(self) -> bool:
        """Check if subscription is active."""
        if self.status != "active":
            return False
        
        if self.end_date and datetime.now() > self.end_date:
            self.status = "expired"
            self.updated_at = datetime.now()
            return False
        
        return True
    
    def is_expired(self) -> bool:
        """Check if subscription is expired."""
        if self.end_date and datetime.now() > self.end_date:
            return True
        return self.status == "expired"
    
    def is_cancelled(self) -> bool:
        """Check if subscription is cancelled."""
        return self.status == "cancelled"
    
    def get_remaining_days(self) -> int:
        """Get remaining days in subscription."""
        if not self.end_date:
            return 0
        
        remaining = self.end_date - datetime.now()
        return max(0, remaining.days)
    
    def get_total_days(self) -> int:
        """Get total duration of subscription in days."""
        if not self.start_date or not self.end_date:
            return 0
        
        duration = self.end_date - self.start_date
        return duration.days

@dataclass
class Invoice:
    """Invoice model class."""
    
    # Invoice identification
    invoice_id: str
    user_id: int
    
    # Invoice details
    amount: float
    currency: str = "TRY"
    plan_name: str = "premium"
    
    # Status
    status: str = "pending"  # pending, paid, expired, cancelled
    
    # Timestamps
    created_at: datetime = None
    paid_at: Optional[datetime] = None
    expires_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
        if self.expires_at is None:
            self.expires_at = datetime.now() + timedelta(hours=24)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert invoice to dictionary."""
        invoice_dict = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in invoice_dict.items():
            if isinstance(value, datetime):
                invoice_dict[key] = value.isoformat()
        
        return invoice_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        """Create invoice from dictionary."""
        # Convert ISO format strings back to datetime objects
        for key in ['created_at', 'paid_at', 'expires_at', 'updated_at']:
            if key in data and data[key]:
                try:
                    data[key] = datetime.fromisoformat(data[key])
                except (ValueError, TypeError):
                    data[key] = None
        
        return cls(**data)
    
    def mark_paid(self) -> None:
        """Mark invoice as paid."""
        self.status = "paid"
        self.paid_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_expired(self) -> None:
        """Mark invoice as expired."""
        self.status = "expired"
        self.updated_at = datetime.now()
    
    def mark_cancelled(self) -> None:
        """Mark invoice as cancelled."""
        self.status = "cancelled"
        self.updated_at = datetime.now()
    
    def is_paid(self) -> bool:
        """Check if invoice is paid."""
        return self.status == "paid"
    
    def is_pending(self) -> bool:
        """Check if invoice is pending."""
        return self.status == "pending"
    
    def is_expired(self) -> bool:
        """Check if invoice is expired."""
        if self.expires_at and datetime.now() > self.expires_at:
            return True
        return self.status == "expired"
    
    def is_cancelled(self) -> bool:
        """Check if invoice is cancelled."""
        return self.status == "cancelled"
    
    def get_formatted_amount(self) -> str:
        """Get formatted amount with currency."""
        return f"{self.amount:.2f} {self.currency}"
    
    def get_remaining_time(self) -> int:
        """Get remaining time in seconds until expiry."""
        if not self.expires_at:
            return 0
        
        remaining = self.expires_at - datetime.now()
        return max(0, int(remaining.total_seconds()))