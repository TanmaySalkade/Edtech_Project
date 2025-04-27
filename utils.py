import random
from models import Reward, Achievement, UserAchievement
from app import db

def calculate_level_progress(user):
    """Calculate the percentage progress to the next level"""
    current_level = user.level
    next_level_xp = current_level * 100  # Simple formula
    current_level_xp = (current_level - 1) * 100 if current_level > 1 else 0
    
    xp_for_current_level = user.xp - current_level_xp
    xp_needed_for_next_level = next_level_xp - current_level_xp
    
    progress_percentage = (xp_for_current_level / xp_needed_for_next_level) * 100
    
    return {
        'current_level': current_level,
        'current_xp': user.xp,
        'xp_for_current_level': xp_for_current_level,
        'xp_needed_for_next_level': xp_needed_for_next_level,
        'progress_percentage': progress_percentage,
        'next_level_xp': next_level_xp
    }

def get_random_reward():
    """Get a random reward based on rarity probability"""
    # Define probability weights for different rarities
    rarities = {
        'Common': 0.70,     # 70% chance
        'Uncommon': 0.20,   # 20% chance
        'Rare': 0.08,       # 8% chance
        'Epic': 0.015,      # 1.5% chance
        'Legendary': 0.005  # 0.5% chance
    }
    
    # Roll for rarity
    roll = random.random()
    cumulative = 0
    selected_rarity = 'Common'  # Default
    
    for rarity, chance in rarities.items():
        cumulative += chance
        if roll <= cumulative:
            selected_rarity = rarity
            break
    
    # Get all rewards of the selected rarity
    rewards = Reward.query.filter_by(rarity=selected_rarity).all()
    
    # If no rewards of that rarity, get a common one
    if not rewards:
        rewards = Reward.query.filter_by(rarity='Common').all()
        
    # If still no rewards, create a default one
    if not rewards:
        default_reward = Reward(
            name='Learning Badge',
            description='A badge for your dedication to learning',
            rarity='Common'
        )
        db.session.add(default_reward)
        db.session.commit()
        return default_reward
    
    # Return a random reward from the filtered list
    return random.choice(rewards)

def check_streak_milestones(user):
    """Check if user has reached a streak milestone and award achievements"""
    streak_milestones = {
        3: "Three-Day Streak",
        7: "Week-Long Streak",
        30: "Monthly Dedication",
        100: "Learning Centurion",
        365: "Year-Round Scholar"
    }
    
    # Check if current streak matches any milestone
    achievement_name = streak_milestones.get(user.streak_days)
    
    if not achievement_name:
        return None
    
    # Check if achievement exists, if not create it
    achievement = Achievement.query.filter_by(name=achievement_name).first()
    if not achievement:
        xp_reward = user.streak_days * 5  # Reward scales with streak length
        achievement = Achievement(
            name=achievement_name,
            description=f"Maintained a learning streak for {user.streak_days} days",
            xp_reward=xp_reward
        )
        db.session.add(achievement)
        db.session.commit()
    
    # Check if user already has this achievement
    user_achievement = UserAchievement.query.filter_by(
        user_id=user.id,
        achievement_id=achievement.id
    ).first()
    
    if not user_achievement:
        # Award the achievement
        user_achievement = UserAchievement(
            user_id=user.id,
            achievement_id=achievement.id
        )
        db.session.add(user_achievement)
        
        # Award XP
        user.add_xp(achievement.xp_reward)
        db.session.commit()
        
        # Return the achievement name to notify user
        return achievement_name
    
    return None

def create_default_rewards():
    """Create default rewards if none exist"""
    if Reward.query.count() == 0:
        default_rewards = [
            {
                'name': 'Learning Star',
                'description': 'A common badge for completing lessons',
                'rarity': 'Common'
            },
            {
                'name': 'Knowledge Token',
                'description': 'A simple token of your learning journey',
                'rarity': 'Common'
            },
            {
                'name': 'Brain Boost',
                'description': 'An uncommon reward for your dedication',
                'rarity': 'Uncommon'
            },
            {
                'name': 'Wisdom Crystal',
                'description': 'A rare crystal that represents your growing wisdom',
                'rarity': 'Rare'
            },
            {
                'name': 'Genius Crown',
                'description': 'An epic reward for exceptional learning',
                'rarity': 'Epic'
            },
            {
                'name': 'Philosopher\'s Stone',
                'description': 'A legendary artifact for masters of knowledge',
                'rarity': 'Legendary'
            }
        ]
        
        for reward_data in default_rewards:
            reward = Reward(**reward_data)
            db.session.add(reward)
        
        db.session.commit()
        return True
    
    return False
