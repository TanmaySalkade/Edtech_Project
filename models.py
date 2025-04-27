from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)
    streak_days = db.Column(db.Integer, default=0)
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    email_notifications = db.Column(db.Boolean, default=True)
    badges = db.Column(db.String(500), default='[]')  # JSON string of earned badges
    
    # Relationships
    course_progress = db.relationship('CourseProgress', backref='user', lazy=True)
    achievements = db.relationship('UserAchievement', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='user', lazy=True)
    
    def get_badges(self):
        """Return the badges as a list"""
        return json.loads(self.badges)
    
    def add_badge(self, badge):
        """Add a badge to the user's badges"""
        badges = self.get_badges()
        if badge not in badges:
            badges.append(badge)
            self.badges = json.dumps(badges)
            return True
        return False
    
    def update_streak(self):
        """Update the user's streak"""
        now = datetime.utcnow()
        # If last login was more than 48 hours ago, reset streak
        if self.last_login and (now - self.last_login) > timedelta(hours=48):
            self.streak_days = 1
        # If last login was within 24-48 hours, increment streak
        elif self.last_login and (now - self.last_login) > timedelta(hours=24):
            self.streak_days += 1
        self.last_login = now
        return self.streak_days
    
    def add_xp(self, amount):
        """Add XP to the user and level up if necessary"""
        self.xp += amount
        
        # Check if user can level up
        xp_threshold = self.level * 100  # Simple formula, adjust as needed
        if self.xp >= xp_threshold:
            self.level += 1
            return True  # Indicates level up
        return False

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    difficulty = db.Column(db.String(20), default='Beginner')  # Beginner, Intermediate, Advanced
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    lessons = db.relationship('Lesson', backref='course', lazy=True, order_by='Lesson.order')
    progress = db.relationship('CourseProgress', backref='course', lazy=True)
    reviews = db.relationship('Review', backref='course', lazy=True)
    
    def average_rating(self):
        """Calculate the average rating for this course"""
        if not self.reviews:
            return 0
        return sum(review.rating for review in self.reviews) / len(self.reviews)

class Lesson(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=True)
    content = db.Column(db.Text, nullable=True)
    youtube_url = db.Column(db.String(200), nullable=True)
    order = db.Column(db.Integer, default=0)  # Order within the course
    xp_reward = db.Column(db.Integer, default=10)  # XP gained for completing
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    completed_by = db.relationship('LessonCompletion', backref='lesson', lazy=True)

class CourseProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    progress_percentage = db.Column(db.Float, default=0.0)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    completed = db.Column(db.Boolean, default=False)
    completed_at = db.Column(db.DateTime)

class LessonCompletion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lesson.id'), nullable=False)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)
    reward_claimed = db.Column(db.Boolean, default=False)

class Achievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    badge_image = db.Column(db.String(200), nullable=True)
    xp_reward = db.Column(db.Integer, default=50)
    
    # Relationship
    earned_by = db.relationship('UserAchievement', backref='achievement', lazy=True)

class UserAchievement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievement.id'), nullable=False)
    earned_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Reward(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    rarity = db.Column(db.String(20), default='Common')  # Common, Uncommon, Rare, Epic, Legendary
    
    def __repr__(self):
        return f'<Reward {self.name}>'
