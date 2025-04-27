from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, IntegerField, HiddenField, FileField, URLField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, URL, NumberRange, Optional
from models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class CourseForm(FlaskForm):
    title = StringField('Course Title', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[DataRequired()])
    image_url = URLField('Image URL', validators=[Optional(), URL()])
    difficulty = SelectField('Difficulty', choices=[
        ('Beginner', 'Beginner'), 
        ('Intermediate', 'Intermediate'), 
        ('Advanced', 'Advanced')
    ])
    submit = SubmitField('Save Course')

class LessonForm(FlaskForm):
    title = StringField('Lesson Title', validators=[DataRequired()])
    description = TextAreaField('Short Description', validators=[DataRequired()])
    content = TextAreaField('Content (Markdown supported)', validators=[Optional()])
    youtube_url = URLField('YouTube Video URL', validators=[Optional(), URL()])
    order = IntegerField('Lesson Order', validators=[DataRequired(), NumberRange(min=1)])
    xp_reward = IntegerField('XP Reward', validators=[DataRequired(), NumberRange(min=1)])
    course_id = HiddenField('Course ID', validators=[DataRequired()])
    submit = SubmitField('Save Lesson')

class ReviewForm(FlaskForm):
    rating = SelectField('Rating', choices=[(1, '1 Star'), (2, '2 Stars'), (3, '3 Stars'), (4, '4 Stars'), (5, '5 Stars')], coerce=int)
    comment = TextAreaField('Your Review', validators=[Optional(), Length(max=500)])
    submit = SubmitField('Submit Review')

class ProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=8)])
    confirm_password = PasswordField('Confirm New Password', validators=[EqualTo('new_password')])
    email_notifications = BooleanField('Email Notifications')
    submit = SubmitField('Update Profile')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user and user.id != self.user_id.data:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user and user.id != self.user_id.data:
            raise ValidationError('Please use a different email address.')
            
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.user_id = HiddenField('user_id')
        if 'user' in kwargs:
            self.user_id.data = kwargs['user'].id
