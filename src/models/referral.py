"""
Referral model for the Fal Gram Bot.
Contains data structures for referral system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Referral:
    """Referral relationship model."""
    
    referrer_id: int
    referred_id: int
    referral_code: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    reward_claimed: bool = False
    reward_claimed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert referral to dictionary."""
        return {
            "referrer_id": self.referrer_id,
            "referred_id": self.referred_id,
            "referral_code": self.referral_code,
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "reward_claimed": self.reward_claimed,
            "reward_claimed_at": self.reward_claimed_at.isoformat() if self.reward_claimed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Referral':
        """Create referral from dictionary."""
        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.fromisoformat(data['created_at'])
            except ValueError:
                pass
        
        reward_claimed_at = None
        if data.get('reward_claimed_at'):
            try:
                reward_claimed_at = datetime.fromisoformat(data['reward_claimed_at'])
            except ValueError:
                pass
        
        return cls(
            referrer_id=data['referrer_id'],
            referred_id=data['referred_id'],
            referral_code=data['referral_code'],
            created_at=created_at,
            is_active=data.get('is_active', True),
            reward_claimed=data.get('reward_claimed', False),
            reward_claimed_at=reward_claimed_at
        )


@dataclass
class ReferralStats:
    """Referral statistics model."""
    
    user_id: int
    total_referrals: int = 0
    active_referrals: int = 0
    total_earnings: int = 0
    referral_code: Optional[str] = None
    referred_by: Optional[str] = None
    last_referral_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert referral stats to dictionary."""
        return {
            "user_id": self.user_id,
            "total_referrals": self.total_referrals,
            "active_referrals": self.active_referrals,
            "total_earnings": self.total_earnings,
            "referral_code": self.referral_code,
            "referred_by": self.referred_by,
            "last_referral_at": self.last_referral_at.isoformat() if self.last_referral_at else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferralStats':
        """Create referral stats from dictionary."""
        last_referral_at = None
        if data.get('last_referral_at'):
            try:
                last_referral_at = datetime.fromisoformat(data['last_referral_at'])
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
        
        return cls(
            user_id=data['user_id'],
            total_referrals=data.get('total_referrals', 0),
            active_referrals=data.get('active_referrals', 0),
            total_earnings=data.get('total_earnings', 0),
            referral_code=data.get('referral_code'),
            referred_by=data.get('referred_by'),
            last_referral_at=last_referral_at,
            created_at=created_at,
            updated_at=updated_at
        )
    
    def get_referral_level(self) -> str:
        """Get user's referral level based on total referrals."""
        if self.total_referrals >= 50:
            return "premium"
        elif self.total_referrals >= 25:
            return "elite"
        elif self.total_referrals >= 10:
            return "vip"
        elif self.total_referrals >= 5:
            return "active"
        else:
            return "new"
    
    def get_next_level_requirements(self) -> Dict[str, Any]:
        """Get requirements for next referral level."""
        current_level = self.get_referral_level()
        
        if current_level == "new":
            return {
                "next_level": "active",
                "required_referrals": 5,
                "remaining": max(0, 5 - self.total_referrals),
                "rewards": ["Weekly bonus readings", "Special profile color"]
            }
        elif current_level == "active":
            return {
                "next_level": "vip",
                "required_referrals": 10,
                "remaining": max(0, 10 - self.total_referrals),
                "rewards": ["VIP tarot deck", "Priority AI responses"]
            }
        elif current_level == "vip":
            return {
                "next_level": "elite",
                "required_referrals": 25,
                "remaining": max(0, 25 - self.total_referrals),
                "rewards": ["Personal reading consultant", "24/7 priority support"]
            }
        elif current_level == "elite":
            return {
                "next_level": "premium",
                "required_referrals": 50,
                "remaining": max(0, 50 - self.total_referrals),
                "rewards": ["Exclusive VIP features", "Special events access"]
            }
        else:
            return {
                "next_level": None,
                "required_referrals": 0,
                "remaining": 0,
                "rewards": ["Maximum level reached"]
            } 