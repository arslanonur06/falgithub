"""
Payment model for the Fal Gram Bot.
Contains data structures for payment and subscription information.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Payment:
    """Payment transaction model."""
    
    payment_id: str
    user_id: int
    amount: float
    currency: str = "TRY"
    payment_method: str = "telegram_stars"
    status: str = "pending"  # pending, completed, failed, refunded
    plan_name: Optional[str] = None
    description: Optional[str] = None
    telegram_payment_charge_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    failed_at: Optional[datetime] = None
    refunded_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert payment to dictionary."""
        return {
            "payment_id": self.payment_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
            "payment_method": self.payment_method,
            "status": self.status,
            "plan_name": self.plan_name,
            "description": self.description,
            "telegram_payment_charge_id": self.telegram_payment_charge_id,
            "created_at": self.created_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "failed_at": self.failed_at.isoformat() if self.failed_at else None,
            "refunded_at": self.refunded_at.isoformat() if self.refunded_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Payment':
        """Create payment from dictionary."""
        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        completed_at = None
        if data.get('completed_at'):
            try:
                completed_at = datetime.fromisoformat(data['completed_at'])
            except ValueError:
                pass
        
        failed_at = None
        if data.get('failed_at'):
            try:
                failed_at = datetime.fromisoformat(data['failed_at'])
            except ValueError:
                pass
        
        refunded_at = None
        if data.get('refunded_at'):
            try:
                refunded_at = datetime.fromisoformat(data['refunded_at'])
            except ValueError:
                pass
        
        return cls(
            payment_id=data['payment_id'],
            user_id=data['user_id'],
            amount=data['amount'],
            currency=data.get('currency', 'TRY'),
            payment_method=data.get('payment_method', 'telegram_stars'),
            status=data.get('status', 'pending'),
            plan_name=data.get('plan_name'),
            description=data.get('description'),
            telegram_payment_charge_id=data.get('telegram_payment_charge_id'),
            created_at=created_at,
            completed_at=completed_at,
            failed_at=failed_at,
            refunded_at=refunded_at
        )


@dataclass
class Subscription:
    """Subscription model."""
    
    subscription_id: str
    user_id: int
    plan_name: str
    status: str = "active"  # active, cancelled, expired
    start_date: datetime = field(default_factory=datetime.now)
    end_date: Optional[datetime] = None
    payment_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    cancelled_at: Optional[datetime] = None
    cancelled_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert subscription to dictionary."""
        return {
            "subscription_id": self.subscription_id,
            "user_id": self.user_id,
            "plan_name": self.plan_name,
            "status": self.status,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "payment_id": self.payment_id,
            "created_at": self.created_at.isoformat(),
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
            "cancelled_reason": self.cancelled_reason
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Subscription':
        """Create subscription from dictionary."""
        start_date = datetime.now()
        if data.get('start_date'):
            try:
                start_date = datetime.fromisoformat(data['start_date'])
            except ValueError:
                pass
        
        end_date = None
        if data.get('end_date'):
            try:
                end_date = datetime.fromisoformat(data['end_date'])
            except ValueError:
                pass
        
        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        cancelled_at = None
        if data.get('cancelled_at'):
            try:
                cancelled_at = datetime.fromisoformat(data['cancelled_at'])
            except ValueError:
                pass
        
        return cls(
            subscription_id=data['subscription_id'],
            user_id=data['user_id'],
            plan_name=data['plan_name'],
            status=data.get('status', 'active'),
            start_date=start_date,
            end_date=end_date,
            payment_id=data.get('payment_id'),
            created_at=created_at,
            cancelled_at=cancelled_at,
            cancelled_reason=data.get('cancelled_reason')
        )
    
    def is_active(self) -> bool:
        """Check if subscription is active."""
        if self.status != "active":
            return False
        
        if not self.end_date:
            return True
        
        return datetime.now() < self.end_date
    
    def get_remaining_days(self) -> int:
        """Get remaining days in subscription."""
        if not self.end_date:
            return -1  # Unlimited
        
        remaining = (self.end_date - datetime.now()).days
        return max(0, remaining)


@dataclass
class Invoice:
    """Invoice model."""
    
    invoice_id: str
    user_id: int
    amount: float
    description: str
    currency: str = "TRY"
    status: str = "pending"  # pending, paid, cancelled, expired
    payment_url: Optional[str] = None
    telegram_invoice_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None
    expired_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert invoice to dictionary."""
        return {
            "invoice_id": self.invoice_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "currency": self.currency,
            "description": self.description,
            "status": self.status,
            "payment_url": self.payment_url,
            "telegram_invoice_id": self.telegram_invoice_id,
            "created_at": self.created_at.isoformat(),
            "paid_at": self.paid_at.isoformat() if self.paid_at else None,
            "expired_at": self.expired_at.isoformat() if self.expired_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Invoice':
        """Create invoice from dictionary."""
        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        paid_at = None
        if data.get('paid_at'):
            try:
                paid_at = datetime.fromisoformat(data['paid_at'])
            except ValueError:
                pass
        
        expired_at = None
        if data.get('expired_at'):
            try:
                expired_at = datetime.fromisoformat(data['expired_at'])
            except ValueError:
                pass
        
        return cls(
            invoice_id=data['invoice_id'],
            user_id=data['user_id'],
            amount=data['amount'],
            currency=data.get('currency', 'TRY'),
            description=data['description'],
            status=data.get('status', 'pending'),
            payment_url=data.get('payment_url'),
            telegram_invoice_id=data.get('telegram_invoice_id'),
            created_at=created_at,
            paid_at=paid_at,
            expired_at=expired_at
        ) 