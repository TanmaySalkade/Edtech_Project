from flask import render_template, redirect, url_for
from app import app, db
from models import Course

@app.route('/')
def home():
    return redirect(url_for('courses'))

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)
