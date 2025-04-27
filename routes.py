from flask import render_template, redirect, url_for
from app import app, db
from models import Course

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/courses')
def courses():
    all_courses = Course.query.all()
    return render_template('courses.html', courses=all_courses)

@app.before_first_request
def create_courses():
    if Course.query.count() == 0:
        python_course = Course(
            title="Python for Beginners",
            description="A complete Python programming playlist.",
            url="https://www.youtube.com/playlist?list=PL1A2CSdiySGJQKniwB3iMdX5T1A8zLabG"
        )
        sql_course = Course(
            title="SQL Tutorial",
            description="Master SQL from basics to advanced.",
            url="https://www.youtube.com/playlist?list=PL1A2CSdiySGK3pJzJz3pL2b1Wz0sbGzQn"
        )
        db.session.add(python_course)
        db.session.add(sql_course)
        db.session.commit()