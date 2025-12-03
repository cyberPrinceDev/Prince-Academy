import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Course

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create DB + seed courses
with app.app_context():
    db.create_all()
    if Course.query.count() == 0:
        courses = [
            Course(title="Full Stack Web Development", description="Master HTML, CSS, JavaScript, Python, Flask & React", price=600000, duration="12 weeks", level="Beginner to Pro"),
            Course(title="UI/UX Design Mastery", description="Learn Figma, user research, prototyping & design thinking", price=350000, duration="10 weeks", level="Beginner"),
            Course(title="Mobile App Development", description="Build iOS & Android apps with React Native", price=400000, duration="10 weeks", level="Intermediate"),
            Course(title="Data Science & Machine Learning", description="Python, Pandas, TensorFlow, and real projects", price=400000, duration="14 weeks", level="Intermediate"),
            Course(title="Digital Marketing", description="SEO, Google Ads, Social Media & Content Strategy", price=250000, duration="8 weeks", level="Beginner"),
            Course(title="Product Management", description="From idea to launch: Agile, Jira, Roadmapping", price=250000, duration="8 weeks", level="All Levels"),
        ]
        db.session.bulk_save_objects(courses)
        db.session.commit()

@app.route('/')
def home():
    courses = Course.query.all()
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return render_template('home.html', courses=courses, user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email'].lower()
        phone = request.form['phone']
        password = request.form['password']

        if User.query.filter_by(email=email).first():
            flash('Email already registered!', 'error')
            return redirect(url_for('register'))

        hashed_pwd = generate_password_hash(password)
        new_user = User(first_name=first_name, last_name=last_name, email=email, phone=phone, password=hashed_pwd)
        db.session.add(new_user)
        db.session.commit()

        flash(f'Welcome, {first_name}! Account created successfully.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email'].lower()
        password = request.form['password']
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash(f'Welcome back, {user.first_name}!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)