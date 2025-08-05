"""
Referral model for the Fal Gram Bot.
"""

from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class Referral:
    """Referral model class."""
    
    # Basic referral info
    referrer_id: int
    referred_id: int
    referral_code: str
    
    # Status and tracking
    status: str = "pending"  # pending, completed, expired
    completed_at: Optional[datetime] = None
    
    # Rewards
    reward_type: str = "premium_days"  # premium_days, coins, etc.
    reward_amount: int = 7  # 7 days premium
    
    # Timestamps
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert referral to dictionary."""
        referral_dict = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in referral_dict.items():
            if isinstance(value, datetime):
                referral_dict[key] = value.isoformat()
        
        return referral_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Referral':
        """Create referral from dictionary."""
        # Convert ISO format strings back to datetime objects
        for key in ['completed_at', 'created_at', 'updated_at']:
            if key in data and data[key]:
                try:
                    data[key] = datetime.fromisoformat(data[key])
                except (ValueError, TypeError):
                    data[key] = None
        
        return cls(**data)
    
    def mark_completed(self) -> None:
        """Mark referral as completed."""
        self.status = "completed"
        self.completed_at = datetime.now()
        self.updated_at = datetime.now()
    
    def mark_expired(self) -> None:
        """Mark referral as expired."""
        self.status = "expired"
        self.updated_at = datetime.now()
    
    def is_completed(self) -> bool:
        """Check if referral is completed."""
        return self.status == "completed"
    
    def is_pending(self) -> bool:
        """Check if referral is pending."""
        return self.status == "pending"
    
    def is_expired(self) -> bool:
        """Check if referral is expired."""
        return self.status == "expired"
    
    def get_reward_description(self) -> str:
        """Get human-readable reward description."""
        if self.reward_type == "premium_days":
            return f"{self.reward_amount} days premium subscription"
        elif self.reward_type == "coins":
            return f"{self.reward_amount} coins"
        else:
            return f"{self.reward_amount} {self.reward_type}"

@dataclass
class ReferralStats:
    """Referral statistics model."""
    
    user_id: int
    total_referrals: int = 0
    completed_referrals: int = 0
    pending_referrals: int = 0
    total_rewards_earned: int = 0
    
    # Level tracking
    current_level: int = 1
    referrals_to_next_level: int = 0
    
    # Timestamps
    last_referral_at: Optional[datetime] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert referral stats to dictionary."""
        stats_dict = asdict(self)
        
        # Convert datetime objects to ISO format strings
        for key, value in stats_dict.items():
            if isinstance(value, datetime):
                stats_dict[key] = value.isoformat()
        
        return stats_dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReferralStats':
        """Create referral stats from dictionary."""
        # Convert ISO format strings back to datetime objects
        for key in ['last_referral_at', 'created_at', 'updated_at']:
            if key in data and data[key]:
                try:
                    data[key] = datetime.fromisoformat(data[key])
                except (ValueError, TypeError):
                    data[key] = None
        
        return cls(**data)
    
    def add_referral(self, status: str = "pending") -> None:
        """Add a new referral."""
        self.total_referrals += 1
        
        if status == "completed":
            self.completed_referrals += 1
        elif status == "pending":
            self.pending_referrals += 1
        
        self.last_referral_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Update level
        self._update_level()
    
    def complete_referral(self) -> None:
        """Complete a pending referral."""
        if self.pending_referrals > 0:
            self.pending_referrals -= 1
            self.completed_referrals += 1
            self.total_rewards_earned += 7  # 7 days premium per referral
            self.updated_at = datetime.now()
            
            # Update level
            self._update_level()
    
    def _update_level(self) -> None:
        """Update user's referral level."""
        # Level thresholds: 1, 3, 5, 10, 20, 50, 100
        level_thresholds = [1, 3, 5, 10, 20, 50, 100]
        
        for i, threshold in enumerate(level_thresholds):
            if self.completed_referrals >= threshold:
                self.current_level = i + 1
        
        # Calculate referrals needed for next level
        next_threshold = None
        for threshold in level_thresholds:
            if self.completed_referrals < threshold:
                next_threshold = threshold
                break
        
        if next_threshold:
            self.referrals_to_next_level = next_threshold - self.completed_referrals
        else:
            self.referrals_to_next_level = 0
    
    def get_level_rewards(self) -> Dict[str, Any]:
        """Get rewards for current level."""
        level_rewards = {
            1: {"premium_days": 7, "description": "7 days premium"},
            2: {"premium_days": 14, "description": "14 days premium"},
            3: {"premium_days": 30, "description": "30 days premium"},
            4: {"premium_days": 60, "description": "60 days premium"},
            5: {"premium_days": 90, "description": "90 days premium"},
            6: {"premium_days": 180, "description": "180 days premium"},
            7: {"premium_days": 365, "description": "365 days premium"}
        }
        
        return level_rewards.get(self.current_level, {"premium_days": 0, "description": "No rewards"})
    
    def get_next_level_info(self) -> Dict[str, Any]:
        """Get information about next level."""
        level_thresholds = [1, 3, 5, 10, 20, 50, 100]
        
        for threshold in level_thresholds:
            if self.completed_referrals < threshold:
                next_level = level_thresholds.index(threshold) + 1
                level_rewards = {
                    1: {"premium_days": 7, "description": "7 days premium"},
                    2: {"premium_days": 14, "description": "14 days premium"},
                    3: {"premium_days": 30, "description": "30 days premium"},
                    4: {"premium_days": 60, "description": "60 days premium"},
                    5: {"premium_days": 90, "description": "90 days premium"},
                    6: {"premium_days": 180, "description": "180 days premium"},
                    7: {"premium_days": 365, "description": "365 days premium"}
                }
                
                return {
                    "level": next_level,
                    "referrals_needed": threshold - self.completed_referrals,
                    "rewards": level_rewards.get(next_level, {"premium_days": 0, "description": "No rewards"})
                }
        
        return {
            "level": self.current_level,
            "referrals_needed": 0,
            "rewards": {"premium_days": 0, "description": "Maximum level reached"}
        }