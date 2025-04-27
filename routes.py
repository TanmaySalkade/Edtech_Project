from flask import render_template, redirect, url_for, flash, request, jsonify, abort
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from models import User, Course, Lesson, CourseProgress, LessonCompletion, Achievement, UserAchievement, Review, Reward
from forms import LoginForm, RegistrationForm, CourseForm, LessonForm, ReviewForm, ProfileForm
from werkzeug.security import generate_password_hash, check_password_hash
from utils import calculate_level_progress, get_random_reward, check_streak_milestones
from email_utils import send_welcome_email, send_streak_reminder, send_achievement_notification
import random
from datetime import datetime, timedelta
import logging

# Context processor to inject variables into all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Home page
@app.route('/')
def index():
    # Get featured courses
    featured_courses = Course.query.limit(3).all()
    return render_template('index.html', featured_courses=featured_courses)

# User authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            # Update streak
            streak_updated = user.update_streak()
            db.session.commit()
            
            # Check if we hit a streak milestone
            streak_achievement = check_streak_milestones(user)
            if streak_achievement:
                flash(f'🏆 Achievement unlocked: {streak_achievement}!', 'success')
            
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/'):
                next_page = url_for('dashboard')
            return redirect(next_page)
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=hashed_password
        )
        db.session.add(user)
        db.session.commit()
        
        # Send welcome email
        send_welcome_email(user)
        
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

# User dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Get courses in progress
    user_progress = CourseProgress.query.filter_by(user_id=current_user.id, completed=False).all()
    
    # Get completed courses
    completed_courses = CourseProgress.query.filter_by(user_id=current_user.id, completed=True).all()
    
    # Get recent achievements
    recent_achievements = UserAchievement.query.filter_by(user_id=current_user.id).order_by(UserAchievement.earned_at.desc()).limit(5).all()
    
    # Calculate level progress
    level_progress = calculate_level_progress(current_user)
    
    return render_template('dashboard.html', 
                          user_progress=user_progress,
                          completed_courses=completed_courses,
                          recent_achievements=recent_achievements,
                          level_progress=level_progress)

# Course routes
@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.route('/course/<int:course_id>')
def course_detail(course_id):
    course = Course.query.get_or_404(course_id)
    
    # If user is logged in, get their progress
    user_progress = None
    if current_user.is_authenticated:
        user_progress = CourseProgress.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        
        # If no progress record exists, create one
        if not user_progress:
            user_progress = CourseProgress(user_id=current_user.id, course_id=course_id)
            db.session.add(user_progress)
            db.session.commit()
    
    # Get reviews
    reviews = Review.query.filter_by(course_id=course_id).order_by(Review.created_at.desc()).all()
    
    # Check if current user has already reviewed
    user_has_reviewed = False
    if current_user.is_authenticated:
        user_has_reviewed = Review.query.filter_by(user_id=current_user.id, course_id=course_id).first() is not None
    
    # Review form
    form = ReviewForm()
    
    return render_template('course_detail.html', 
                          course=course, 
                          user_progress=user_progress,
                          reviews=reviews,
                          user_has_reviewed=user_has_reviewed,
                          form=form)

@app.route('/lesson/<int:lesson_id>')
@login_required
def lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Get user progress for this course
    user_progress = CourseProgress.query.filter_by(user_id=current_user.id, course_id=lesson.course_id).first()
    
    # If no progress record exists, create one
    if not user_progress:
        user_progress = CourseProgress(user_id=current_user.id, course_id=lesson.course_id)
        db.session.add(user_progress)
        db.session.commit()
    
    # Check if lesson is already completed
    lesson_completed = LessonCompletion.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first() is not None
    
    # Update last accessed time
    user_progress.last_accessed = datetime.utcnow()
    db.session.commit()
    
    # Get next and previous lessons
    next_lesson = Lesson.query.filter(Lesson.course_id == lesson.course_id, Lesson.order > lesson.order).order_by(Lesson.order).first()
    prev_lesson = Lesson.query.filter(Lesson.course_id == lesson.course_id, Lesson.order < lesson.order).order_by(Lesson.order.desc()).first()
    
    return render_template('lesson.html', 
                          lesson=lesson, 
                          user_progress=user_progress,
                          lesson_completed=lesson_completed,
                          next_lesson=next_lesson,
                          prev_lesson=prev_lesson)

@app.route('/complete_lesson/<int:lesson_id>', methods=['POST'])
@login_required
def complete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    
    # Check if lesson is already completed
    completion = LessonCompletion.query.filter_by(user_id=current_user.id, lesson_id=lesson_id).first()
    if completion:
        return jsonify({
            'success': False,
            'message': 'Lesson already completed'
        })
    
    # Mark lesson as completed
    completion = LessonCompletion(user_id=current_user.id, lesson_id=lesson_id)
    db.session.add(completion)
    
    # Add XP to user
    level_up = current_user.add_xp(lesson.xp_reward)
    
    # Update course progress
    user_progress = CourseProgress.query.filter_by(user_id=current_user.id, course_id=lesson.course_id).first()
    
    # Calculate new progress percentage
    total_lessons = Lesson.query.filter_by(course_id=lesson.course_id).count()
    completed_lessons = LessonCompletion.query.join(Lesson).filter(
        LessonCompletion.user_id == current_user.id,
        Lesson.course_id == lesson.course_id
    ).count()
    
    user_progress.progress_percentage = (completed_lessons / total_lessons) * 100
    
    # Check if course is completed
    if user_progress.progress_percentage >= 100:
        user_progress.completed = True
        user_progress.completed_at = datetime.utcnow()
        
        # Add bonus XP for completing course
        current_user.add_xp(50)  # Bonus XP for course completion
        
        # Check if we need to create any achievements
        achievement = Achievement.query.filter_by(name=f"Completed: {lesson.course.title}").first()
        if not achievement:
            achievement = Achievement(
                name=f"Completed: {lesson.course.title}",
                description=f"Successfully completed the {lesson.course.title} course",
                xp_reward=50
            )
            db.session.add(achievement)
            db.session.flush()  # To get the ID without committing
        
        # Give the achievement to the user if they don't have it
        user_achievement = UserAchievement.query.filter_by(
            user_id=current_user.id, 
            achievement_id=achievement.id
        ).first()
        
        if not user_achievement:
            user_achievement = UserAchievement(
                user_id=current_user.id,
                achievement_id=achievement.id
            )
            db.session.add(user_achievement)
            current_user.add_xp(achievement.xp_reward)
    
    # Get random reward
    reward = None
    if random.random() < 0.3:  # 30% chance of getting a reward
        reward = get_random_reward()
    
    db.session.commit()
    
    # Prepare response
    response = {
        'success': True,
        'xpGained': lesson.xp_reward,
        'levelUp': level_up,
        'courseProgress': user_progress.progress_percentage,
        'courseCompleted': user_progress.completed,
        'currentLevel': current_user.level,
        'currentXP': current_user.xp,
        'reward': reward.name if reward else None
    }
    
    return jsonify(response)

@app.route('/submit_review/<int:course_id>', methods=['POST'])
@login_required
def submit_review(course_id):
    form = ReviewForm()
    if form.validate_on_submit():
        # Check if user has already reviewed this course
        existing_review = Review.query.filter_by(user_id=current_user.id, course_id=course_id).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = form.rating.data
            existing_review.comment = form.comment.data
            existing_review.updated_at = datetime.utcnow()
            flash('Your review has been updated!', 'success')
        else:
            # Create new review
            review = Review(
                user_id=current_user.id,
                course_id=course_id,
                rating=form.rating.data,
                comment=form.comment.data
            )
            db.session.add(review)
            
            # Award XP for leaving a review
            current_user.add_xp(5)
            flash('Your review has been submitted! You earned 5 XP.', 'success')
        
        db.session.commit()
    
    return redirect(url_for('course_detail', course_id=course_id))

# Profile routes
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    
    if form.validate_on_submit():
        # If current password is provided, validate it before updating
        if form.current_password.data:
            if check_password_hash(current_user.password_hash, form.current_password.data):
                # If new password is provided, update it
                if form.new_password.data:
                    current_user.password_hash = generate_password_hash(form.new_password.data)
            else:
                flash('Current password is incorrect', 'danger')
                return render_template('profile.html', form=form)
        
        # Update other fields
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.email_notifications = form.email_notifications.data
        
        db.session.commit()
        flash('Profile updated successfully', 'success')
        return redirect(url_for('profile'))
    
    # Get user achievements
    achievements = UserAchievement.query.filter_by(user_id=current_user.id).all()
    
    # Calculate level progress
    level_progress = calculate_level_progress(current_user)
    
    return render_template('profile.html', 
                          form=form, 
                          user=current_user, 
                          achievements=achievements,
                          level_progress=level_progress)

# Admin routes
@app.route('/admin')
@login_required
def admin_index():
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges.', 'danger')
        return redirect(url_for('dashboard'))
    
    # Get basic stats
    total_users = User.query.count()
    total_courses = Course.query.count()
    total_lessons = Lesson.query.count()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/index.html', 
                          total_users=total_users,
                          total_courses=total_courses,
                          total_lessons=total_lessons,
                          recent_users=recent_users)

@app.route('/admin/courses', methods=['GET', 'POST'])
@login_required
def admin_courses():
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges.', 'danger')
        return redirect(url_for('dashboard'))
    
    form = CourseForm()
    if form.validate_on_submit():
        course = Course(
            title=form.title.data,
            description=form.description.data,
            image_url=form.image_url.data,
            difficulty=form.difficulty.data
        )
        db.session.add(course)
        db.session.commit()
        
        flash('Course created successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    courses = Course.query.all()
    return render_template('admin/courses.html', form=form, courses=courses)

@app.route('/admin/edit_course/<int:course_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_course(course_id):
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges.', 'danger')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    form = CourseForm(obj=course)
    
    if form.validate_on_submit():
        course.title = form.title.data
        course.description = form.description.data
        course.image_url = form.image_url.data
        course.difficulty = form.difficulty.data
        
        db.session.commit()
        flash('Course updated successfully!', 'success')
        return redirect(url_for('admin_courses'))
    
    return render_template('admin/courses.html', form=form, courses=Course.query.all(), editing=course)

@app.route('/admin/delete_course/<int:course_id>', methods=['POST'])
@login_required
def admin_delete_course(course_id):
    if not current_user.is_admin:
        abort(403)
    
    course = Course.query.get_or_404(course_id)
    
    # Delete all related lessons
    Lesson.query.filter_by(course_id=course_id).delete()
    
    # Delete all progress records
    CourseProgress.query.filter_by(course_id=course_id).delete()
    
    # Delete all reviews
    Review.query.filter_by(course_id=course_id).delete()
    
    # Finally delete the course
    db.session.delete(course)
    db.session.commit()
    
    flash('Course deleted successfully', 'success')
    return redirect(url_for('admin_courses'))

@app.route('/admin/lessons/<int:course_id>', methods=['GET', 'POST'])
@login_required
def admin_lessons(course_id):
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges.', 'danger')
        return redirect(url_for('dashboard'))
    
    course = Course.query.get_or_404(course_id)
    form = LessonForm()
    form.course_id.data = course_id
    
    if form.validate_on_submit():
        lesson = Lesson(
            course_id=course_id,
            title=form.title.data,
            description=form.description.data,
            content=form.content.data,
            youtube_url=form.youtube_url.data,
            order=form.order.data,
            xp_reward=form.xp_reward.data
        )
        db.session.add(lesson)
        db.session.commit()
        
        flash('Lesson created successfully!', 'success')
        return redirect(url_for('admin_lessons', course_id=course_id))
    
    lessons = Lesson.query.filter_by(course_id=course_id).order_by(Lesson.order).all()
    return render_template('admin/lessons.html', form=form, course=course, lessons=lessons)

@app.route('/admin/edit_lesson/<int:lesson_id>', methods=['GET', 'POST'])
@login_required
def admin_edit_lesson(lesson_id):
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges.', 'danger')
        return redirect(url_for('dashboard'))
    
    lesson = Lesson.query.get_or_404(lesson_id)
    form = LessonForm(obj=lesson)
    
    if form.validate_on_submit():
        lesson.title = form.title.data
        lesson.description = form.description.data
        lesson.content = form.content.data
        lesson.youtube_url = form.youtube_url.data
        lesson.order = form.order.data
        lesson.xp_reward = form.xp_reward.data
        
        db.session.commit()
        flash('Lesson updated successfully!', 'success')
        return redirect(url_for('admin_lessons', course_id=lesson.course_id))
    
    return render_template('admin/lessons.html', 
                          form=form, 
                          course=lesson.course, 
                          lessons=Lesson.query.filter_by(course_id=lesson.course_id).order_by(Lesson.order).all(),
                          editing=lesson)

@app.route('/admin/delete_lesson/<int:lesson_id>', methods=['POST'])
@login_required
def admin_delete_lesson(lesson_id):
    if not current_user.is_admin:
        abort(403)
    
    lesson = Lesson.query.get_or_404(lesson_id)
    course_id = lesson.course_id
    
    # Delete all completion records
    LessonCompletion.query.filter_by(lesson_id=lesson_id).delete()
    
    # Delete the lesson
    db.session.delete(lesson)
    db.session.commit()
    
    flash('Lesson deleted successfully', 'success')
    return redirect(url_for('admin_lessons', course_id=course_id))

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        flash('Access denied. You need admin privileges.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/toggle_admin/<int:user_id>', methods=['POST'])
@login_required
def admin_toggle_admin(user_id):
    if not current_user.is_admin or current_user.id == user_id:
        abort(403)  # Prevent self-demotion
    
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = "granted" if user.is_admin else "revoked"
    flash(f'Admin privileges {status} for {user.username}', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@login_required
def admin_delete_user(user_id):
    if not current_user.is_admin or current_user.id == user_id:
        abort(403)  # Prevent self-deletion
    
    user = User.query.get_or_404(user_id)
    
    # Delete all user's data
    CourseProgress.query.filter_by(user_id=user_id).delete()
    LessonCompletion.query.filter_by(user_id=user_id).delete()
    UserAchievement.query.filter_by(user_id=user_id).delete()
    Review.query.filter_by(user_id=user_id).delete()
    
    # Delete the user
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.username} has been deleted', 'success')
    return redirect(url_for('admin_users'))

# Send streak reminders
@app.route('/send_streak_reminders', methods=['GET'])
def send_streak_reminders():
    # This route should be protected or called via cron job
    if not request.args.get('key') == os.environ.get('API_KEY', 'default_key'):
        abort(403)
    
    # Find users who haven't logged in for between 20 and 24 hours
    cutoff_time = datetime.utcnow() - timedelta(hours=20)
    reminder_time = datetime.utcnow() - timedelta(hours=24)
    
    users_to_remind = User.query.filter(
        User.email_notifications == True,
        User.last_login <= cutoff_time,
        User.last_login >= reminder_time,
        User.streak_days > 0
    ).all()
    
    count = 0
    for user in users_to_remind:
        if send_streak_reminder(user):
            count += 1
    
    return jsonify({'success': True, 'reminders_sent': count})

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500
