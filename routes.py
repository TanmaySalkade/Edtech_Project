from flask import render_template
from app import app

@app.route('/courses')
def courses():
    courses = [
        {
            "title": "Python for Beginners",
            "description": "A complete Python programming playlist.",
            "url": "https://www.youtube.com/playlist?list=PL1A2CSdiySGJQKniwB3iMdX5T1A8zLabG"
        },
        {
            "title": "SQL Tutorial",
            "description": "Master SQL from basics to advanced.",
            "url": "https://www.youtube.com/playlist?list=PL1A2CSdiySGK3pJzJz3pL2b1Wz0sbGzQn"
        }
    ]
    return render_template('courses.html', courses=courses)