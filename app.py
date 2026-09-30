"""
AI-Powered Learning Management System - Backend
Flask application with AI integration for personalized learning
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import json
from functools import wraps
import jwt
import re

# Initialize Flask App
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///ai_lms.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Extensions
db = SQLAlchemy(app)
CORS(app)

# ==================== Database Models ====================

class User(db.Model):
    """User model for authentication and profile management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    learning_goal = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    enrollments = db.relationship('Enrollment', backref='user', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('UserProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'learning_goal': self.learning_goal,
            'created_at': self.created_at.isoformat()
        }


class Course(db.Model):
    """Course model"""
    __tablename__ = 'courses'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    level = db.Column(db.String(50), nullable=False)  # beginner, intermediate, advanced
    duration_hours = db.Column(db.Integer, default=0)
    instructor = db.Column(db.String(120), nullable=False)
    rating = db.Column(db.Float, default=0.0)
    students_count = db.Column(db.Integer, default=0)
    content = db.Column(db.Text)  # Course content
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('Module', backref='course', lazy=True, cascade='all, delete-orphan')
    enrollments = db.relationship('Enrollment', backref='course', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'category': self.category,
            'level': self.level,
            'duration_hours': self.duration_hours,
            'instructor': self.instructor,
            'rating': self.rating,
            'students_count': self.students_count,
            'created_at': self.created_at.isoformat()
        }


class Module(db.Model):
    """Course module model"""
    __tablename__ = 'modules'
    
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)
    video_url = db.Column(db.String(500))
    duration_minutes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'title': self.title,
            'description': self.description,
            'order': self.order,
            'duration_minutes': self.duration_minutes,
            'created_at': self.created_at.isoformat()
        }


class Enrollment(db.Model):
    """User course enrollment"""
    __tablename__ = 'enrollments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    is_completed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'enrolled_at': self.enrolled_at.isoformat(),
            'is_completed': self.is_completed
        }


class UserProgress(db.Model):
    """Track user progress in courses"""
    __tablename__ = 'user_progress'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('modules.id'))
    progress_percentage = db.Column(db.Float, default=0.0)
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)
    time_spent_minutes = db.Column(db.Integer, default=0)
    is_module_completed = db.Column(db.Boolean, default=False)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'course_id': self.course_id,
            'progress_percentage': self.progress_percentage,
            'time_spent_minutes': self.time_spent_minutes,
            'is_module_completed': self.is_module_completed
        }


class AITutorChat(db.Model):
    """Store AI tutor conversation history"""
    __tablename__ = 'ai_tutor_chat'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_message = db.Column(db.Text, nullable=False)
    ai_response = db.Column(db.Text, nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))
    topic = db.Column(db.String(200))
    rating = db.Column(db.Integer)  # User rating of response
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# ==================== Authentication Routes ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        # Validate input
        if not all(k in data for k in ['username', 'email', 'password']):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Check if user exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Username already exists'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', '')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User registered successfully',
            'user': user.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing email or password'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate JWT token
        token = jwt.encode(
            {
                'user_id': user.id,
                'exp': datetime.utcnow() + timedelta(days=30)
            },
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Decorator for Token Verification ====================

def token_required(f):
    """Decorator to verify JWT token"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Missing token'}), 401
        
        try:
            token = token.split(' ')[1]  # Remove 'Bearer '
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'error': 'Invalid token'}), 401
        
        return f(current_user_id, *args, **kwargs)
    
    return decorated


# ==================== Course Routes ====================

@app.route('/api/courses', methods=['GET'])
def get_courses():
    """Get all courses with optional filtering"""
    try:
        category = request.args.get('category')
        level = request.args.get('level')
        search = request.args.get('search', '').lower()
        
        query = Course.query
        
        if category:
            query = query.filter_by(category=category)
        
        if level:
            query = query.filter_by(level=level)
        
        if search:
            query = query.filter(
                (Course.title.ilike(f'%{search}%')) |
                (Course.description.ilike(f'%{search}%'))
            )
        
        courses = query.all()
        return jsonify([course.to_dict() for course in courses]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/courses/<int:course_id>', methods=['GET'])
def get_course(course_id):
    """Get course details"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404
        
        course_dict = course.to_dict()
        course_dict['modules'] = [module.to_dict() for module in course.modules]
        
        return jsonify(course_dict), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/courses', methods=['POST'])
@token_required
def create_course(current_user_id):
    """Create a new course (admin only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['title', 'description', 'category', 'level', 'instructor']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        course = Course(
            title=data['title'],
            description=data['description'],
            category=data['category'],
            level=data['level'],
            duration_hours=data.get('duration_hours', 0),
            instructor=data['instructor'],
            content=data.get('content', '')
        )
        
        db.session.add(course)
        db.session.commit()
        
        return jsonify({
            'message': 'Course created successfully',
            'course': course.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== Enrollment Routes ====================

@app.route('/api/enrollments', methods=['POST'])
@token_required
def enroll_course(current_user_id):
    """Enroll user in a course"""
    try:
        data = request.get_json()
        course_id = data.get('course_id')
        
        if not course_id:
            return jsonify({'error': 'Course ID required'}), 400
        
        # Check if already enrolled
        existing = Enrollment.query.filter_by(
            user_id=current_user_id,
            course_id=course_id
        ).first()
        
        if existing:
            return jsonify({'error': 'Already enrolled in this course'}), 400
        
        # Create enrollment
        enrollment = Enrollment(
            user_id=current_user_id,
            course_id=course_id
        )
        
        db.session.add(enrollment)
        db.session.commit()
        
        return jsonify({
            'message': 'Enrolled successfully',
            'enrollment': enrollment.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@app.route('/api/enrollments', methods=['GET'])
@token_required
def get_enrollments(current_user_id):
    """Get user's enrollments"""
    try:
        enrollments = Enrollment.query.filter_by(user_id=current_user_id).all()
        enrollment_list = []
        
        for enrollment in enrollments:
            enr_dict = enrollment.to_dict()
            enr_dict['course'] = enrollment.course.to_dict()
            enrollment_list.append(enr_dict)
        
        return jsonify(enrollment_list), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== Progress Routes ====================

@app.route('/api/progress/<int:course_id>', methods=['GET'])
@token_required
def get_progress(current_user_id, course_id):
    """Get user progress in a course"""
    try:
        progress = UserProgress.query.filter_by(
            user_id=current_user_id,
            course_id=course_id
        ).all()
        
        return jsonify([p.to_dict() for p in progress]), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/progress', methods=['POST'])
@token_required
def update_progress(current_user_id):
    """Update user progress"""
    try:
        data = request.get_json()
        
        required_fields = ['course_id', 'progress_percentage']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Find or create progress record
        progress = UserProgress.query.filter_by(
            user_id=current_user_id,
            course_id=data['course_id'],
            module_id=data.get('module_id')
        ).first()
        
        if not progress:
            progress = UserProgress(
                user_id=current_user_id,
                course_id=data['course_id'],
                module_id=data.get('module_id')
            )
            db.session.add(progress)
        
        progress.progress_percentage = data['progress_percentage']
        progress.last_accessed = datetime.utcnow()
        progress.time_spent_minutes = data.get('time_spent_minutes', progress.time_spent_minutes)
        progress.is_module_completed = data.get('is_module_completed', False)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Progress updated successfully',
            'progress': progress.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== AI Tutor Routes ====================

@app.route('/api/ai-tutor/chat', methods=['POST'])
@token_required
def ai_tutor_chat(current_user_id):
    """AI tutor chat endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get AI response
        ai_response = generate_ai_response(user_message, current_user_id)
        
        # Store conversation
        chat = AITutorChat(
            user_id=current_user_id,
            user_message=user_message,
            ai_response=ai_response,
            topic=extract_topic(user_message)
        )
        
        db.session.add(chat)
        db.session.commit()
        
        return jsonify({
            'user_message': user_message,
            'ai_response': ai_response,
            'chat_id': chat.id
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def generate_ai_response(user_message, user_id):
    """Generate AI tutor response based on user message"""
    user_msg_lower = user_message.lower()
    
    # Define response patterns
    responses = {
        'python': 'Python is a versatile programming language. Key topics include: variables, data types, functions, loops, and object-oriented programming. What specific aspect would you like to learn?',
        'javascript': 'JavaScript is essential for web development. It handles interactivity on websites. Topics include: DOM manipulation, callbacks, promises, async/await, and frameworks like React.',
        'machine learning': 'Machine Learning enables computers to learn from data. Main types: supervised learning (classification, regression), unsupervised learning (clustering), and reinforcement learning.',
        'web development': 'Web development involves frontend (HTML, CSS, JavaScript, frameworks) and backend (servers, databases, APIs). Start with HTML/CSS basics, then add JavaScript interactivity.',
        'database': 'Databases store and manage data. Types: relational (SQL), NoSQL (MongoDB), graph databases. SQL is most common for structured data.',
        'api': 'An API (Application Programming Interface) allows different software to communicate. REST APIs are most common, using HTTP methods: GET, POST, PUT, DELETE.',
        'how do i': 'I\'m here to help! Could you be more specific about what you want to learn? For example: "How do I create a function in Python?" or "How do I use React?"',
    }
    
    # Check for keyword matches
    for keyword, response in responses.items():
        if keyword in user_msg_lower:
            return response
    
    # Default response
    return 'That\'s a great question! To give you the best answer, could you provide more context? Tell me more about what you\'re trying to learn or achieve.'


def extract_topic(message):
    """Extract the main topic from user message"""
    topics = ['python', 'javascript', 'web', 'machine learning', 'data', 'api', 'database']
    message_lower = message.lower()
    
    for topic in topics:
        if topic in message_lower:
            return topic
    
    return 'general'


# ==================== User Profile Routes ====================

@app.route('/api/users/profile', methods=['GET'])
@token_required
def get_profile(current_user_id):
    """Get user profile"""
    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile = user.to_dict()
        
        # Add statistics
        enrollments = Enrollment.query.filter_by(user_id=current_user_id).all()
        profile['total_courses'] = len(enrollments)
        profile['completed_courses'] = len([e for e in enrollments if e.is_completed])
        
        # Calculate total learning hours
        progress_records = UserProgress.query.filter_by(user_id=current_user_id).all()
        profile['total_learning_hours'] = sum(p.time_spent_minutes for p in progress_records) / 60
        
        return jsonify(profile), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/users/profile', methods=['PUT'])
@token_required
def update_profile(current_user_id):
    """Update user profile"""
    try:
        user = User.query.get(current_user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'learning_goal' in data:
            user.learning_goal = data['learning_goal']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ==================== Statistics Routes ====================

@app.route('/api/stats', methods=['GET'])
@token_required
def get_stats(current_user_id):
    """Get user learning statistics"""
    try:
        user = User.query.get(current_user_id)
        enrollments = Enrollment.query.filter_by(user_id=current_user_id).all()
        progress_records = UserProgress.query.filter_by(user_id=current_user_id).all()
        
        stats = {
            'active_courses': len([e for e in enrollments if not e.is_completed]),
            'completed_courses': len([e for e in enrollments if e.is_completed]),
            'total_courses': len(enrollments),
            'total_learning_hours': sum(p.time_spent_minutes for p in progress_records) / 60,
            'average_progress': sum(p.progress_percentage for p in progress_records) / len(progress_records) if progress_records else 0,
            'learning_streak': calculate_learning_streak(current_user_id)
        }
        
        return jsonify(stats), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def calculate_learning_streak(user_id):
    """Calculate user's learning streak in days"""
    progress = UserProgress.query.filter_by(user_id=user_id).order_by(
        UserProgress.last_accessed.desc()
    ).all()
    
    if not progress:
        return 0
    
    streak = 0
    today = datetime.utcnow().date()
    
    for i, p in enumerate(progress):
        expected_date = today - timedelta(days=i)
        if p.last_accessed.date() == expected_date:
            streak += 1
        else:
            break
    
    return streak


# ==================== Database Initialization ====================

@app.before_request
def create_tables():
    """Create database tables if they don't exist"""
    if not hasattr(app, 'db_initialized'):
        db.create_all()
        app.db_initialized = True


# ==================== Error Handlers ====================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500


# ==================== Health Check ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'}), 200


# ==================== Run Application ====================

if __name__ == '__main__':
    # Create app context and initialize database
    with app.app_context():
        db.create_all()
        
        # Add sample data if database is empty
        if Course.query.first() is None:
            sample_courses = [
                Course(
                    title='Python Fundamentals',
                    description='Learn Python basics from scratch',
                    category='python',
                    level='beginner',
                    duration_hours=40,
                    instructor='John Smith',
                    rating=4.8,
                    students_count=15420
                ),
                Course(
                    title='Machine Learning Basics',
                    description='Introduction to ML concepts and algorithms',
                    category='ai',
                    level='intermediate',
                    duration_hours=60,
                    instructor='Jane Doe',
                    rating=4.9,
                    students_count=12300
                ),
                Course(
                    title='Web Development with React',
                    description='Build modern web applications with React',
                    category='web',
                    level='intermediate',
                    duration_hours=50,
                    instructor='Bob Johnson',
                    rating=4.7,
                    students_count=18900
                ),
            ]
            
            for course in sample_courses:
                db.session.add(course)
            
            db.session.commit()
    
    app.run(debug=True, host='0.0.0.0', port=5000)


