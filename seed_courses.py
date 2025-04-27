from app import app, db
from models import Course, Lesson
from datetime import datetime
import json

# Course data with lessons from YouTube playlists
courses_data = [
    {
        "title": "Python for Beginners",
        "description": "A comprehensive Python course for beginners. Learn Python from scratch and build a strong foundation in programming with this step-by-step tutorial series.",
        "image_url": "https://i.ytimg.com/vi/kqtD5dpn9C8/maxresdefault.jpg",
        "difficulty": "Beginner",
        "lessons": [
            {
                "title": "Python for Beginners - Learn Python in 1 Hour",
                "description": "This Python tutorial helps beginners learn Python programming from scratch in just one hour.",
                "youtube_url": "https://www.youtube.com/watch?v=kqtD5dpn9C8",
                "order": 1,
                "xp_reward": 20
            },
            {
                "title": "Python Functions",
                "description": "Learn how to create and use functions in Python, including parameters, return values, and scope.",
                "youtube_url": "https://www.youtube.com/watch?v=9Os0o3wzS_I",
                "order": 2,
                "xp_reward": 20
            },
            {
                "title": "Python Lists and Loops",
                "description": "Explore Python lists, list methods, and how to iterate through lists using loops.",
                "youtube_url": "https://www.youtube.com/watch?v=6iF8Xb7Z3wQ",
                "order": 3,
                "xp_reward": 25
            },
            {
                "title": "Python Classes and Objects",
                "description": "Introduction to object-oriented programming in Python with classes, objects, and inheritance.",
                "youtube_url": "https://www.youtube.com/watch?v=apACNr7DC_s",
                "order": 4,
                "xp_reward": 30
            },
            {
                "title": "Python Error Handling",
                "description": "Learn how to handle errors and exceptions in Python to make your programs more robust.",
                "youtube_url": "https://www.youtube.com/watch?v=NIWwJbo-9_8",
                "order": 5,
                "xp_reward": 25
            }
        ]
    },
    {
        "title": "Machine Learning Fundamentals",
        "description": "Learn the core concepts of machine learning, including supervised and unsupervised learning, model evaluation, and practical applications with Python libraries.",
        "image_url": "https://i.ytimg.com/vi/7eh4d6sabA0/maxresdefault.jpg",
        "difficulty": "Intermediate",
        "lessons": [
            {
                "title": "Machine Learning Crash Course for Beginners",
                "description": "A comprehensive introduction to machine learning concepts and terminology.",
                "youtube_url": "https://www.youtube.com/watch?v=ngLyX54e1LU",
                "order": 1,
                "xp_reward": 30
            },
            {
                "title": "Linear Regression in Python",
                "description": "Learn how to implement linear regression models using Python's scikit-learn library.",
                "youtube_url": "https://www.youtube.com/watch?v=NUXdtN1W1FE",
                "order": 2,
                "xp_reward": 35
            },
            {
                "title": "Classification Algorithms",
                "description": "Explore different classification algorithms including logistic regression, decision trees, and random forests.",
                "youtube_url": "https://www.youtube.com/watch?v=pYxNSUDSFH4",
                "order": 3,
                "xp_reward": 40
            },
            {
                "title": "Clustering and Unsupervised Learning",
                "description": "Introduction to clustering algorithms and unsupervised machine learning techniques.",
                "youtube_url": "https://www.youtube.com/watch?v=5cOhL4B5waU",
                "order": 4,
                "xp_reward": 40
            },
            {
                "title": "Neural Networks and Deep Learning Basics",
                "description": "An introduction to neural networks, deep learning, and how to implement them using TensorFlow.",
                "youtube_url": "https://www.youtube.com/watch?v=aircAruvnKk",
                "order": 5,
                "xp_reward": 50
            }
        ]
    },
    {
        "title": "SQL for Data Analysis",
        "description": "Master SQL for data analysis, from basic queries to advanced techniques. Learn how to retrieve, filter, join, and analyze data from relational databases.",
        "image_url": "https://i.ytimg.com/vi/HXV3zeQKqGY/maxresdefault.jpg",
        "difficulty": "Beginner",
        "lessons": [
            {
                "title": "SQL Basics - SELECT, WHERE, ORDER BY",
                "description": "Learn the fundamentals of SQL queries including SELECT statements, WHERE clauses, and sorting results.",
                "youtube_url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
                "order": 1,
                "xp_reward": 20
            },
            {
                "title": "SQL JOIN Types and Examples",
                "description": "Understanding different types of JOINs in SQL and when to use them.",
                "youtube_url": "https://www.youtube.com/watch?v=9yeOJ0ZMUYw",
                "order": 2,
                "xp_reward": 25
            },
            {
                "title": "SQL Aggregation and GROUP BY",
                "description": "Learn how to use aggregate functions and GROUP BY to summarize data.",
                "youtube_url": "https://www.youtube.com/watch?v=Jh_pvk48jHA",
                "order": 3,
                "xp_reward": 25
            },
            {
                "title": "Subqueries and Common Table Expressions (CTEs)",
                "description": "Advanced SQL techniques including subqueries and CTEs for complex data analysis.",
                "youtube_url": "https://www.youtube.com/watch?v=m1KcNV-Zhmc",
                "order": 4,
                "xp_reward": 30
            },
            {
                "title": "SQL Window Functions",
                "description": "Using window functions to perform calculations across rows related to the current row.",
                "youtube_url": "https://www.youtube.com/watch?v=H6OTMoXjNiM",
                "order": 5,
                "xp_reward": 35
            }
        ]
    },
    {
        "title": "Data Science with Python",
        "description": "Learn essential data science skills with Python, covering data manipulation, visualization, analysis, and machine learning applications with real-world datasets.",
        "image_url": "https://i.ytimg.com/vi/ua-CiDNNj30/maxresdefault.jpg",
        "difficulty": "Intermediate",
        "lessons": [
            {
                "title": "Introduction to Data Science with Python",
                "description": "Overview of the data science field and Python libraries for data analysis.",
                "youtube_url": "https://www.youtube.com/watch?v=ua-CiDNNj30",
                "order": 1,
                "xp_reward": 25
            },
            {
                "title": "Data Analysis with Pandas",
                "description": "Learn to use Pandas for data manipulation, cleaning, and analysis.",
                "youtube_url": "https://www.youtube.com/watch?v=vmEHCJofslg",
                "order": 2,
                "xp_reward": 30
            },
            {
                "title": "Data Visualization with Matplotlib and Seaborn",
                "description": "Creating effective visualizations with Python's popular plotting libraries.",
                "youtube_url": "https://www.youtube.com/watch?v=a9UrKTVEeZA",
                "order": 3,
                "xp_reward": 30
            },
            {
                "title": "Exploratory Data Analysis (EDA)",
                "description": "Techniques for exploring and understanding datasets before applying machine learning.",
                "youtube_url": "https://www.youtube.com/watch?v=xi0vhXFPegw",
                "order": 4,
                "xp_reward": 35
            },
            {
                "title": "Predictive Modeling and Machine Learning Projects",
                "description": "End-to-end data science projects implementing predictive models on real-world data.",
                "youtube_url": "https://www.youtube.com/watch?v=fwY9Qv96DJY",
                "order": 5,
                "xp_reward": 40
            }
        ]
    }
]

def seed_courses():
    with app.app_context():
        # Add each course and its lessons
        for course_data in courses_data:
            # Check if the course already exists by title
            existing_course = Course.query.filter_by(title=course_data['title']).first()
            
            if not existing_course:
                # Create new course
                lessons_data = course_data.pop('lessons')
                new_course = Course(**course_data)
                db.session.add(new_course)
                db.session.flush()  # Flush to get the course ID
                
                # Add lessons for this course
                for lesson_data in lessons_data:
                    lesson_data['course_id'] = new_course.id
                    new_lesson = Lesson(**lesson_data)
                    db.session.add(new_lesson)
                
                print(f"Added course: {new_course.title} with {len(lessons_data)} lessons")
            else:
                print(f"Course '{course_data['title']}' already exists, skipping")
        
        # Commit all changes
        db.session.commit()
        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_courses()