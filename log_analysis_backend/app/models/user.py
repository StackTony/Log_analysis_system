from datetime import datetime
from flask_bcrypt import Bcrypt
from app import db

# 创建Bcrypt实例
bcrypt = Bcrypt()

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')  # admin/user
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    check_items = db.relationship('CheckItem', backref='creator', lazy=True)
    cases = db.relationship('Case', backref='processor', lazy=True)
    reports = db.relationship('AnalysisReport', backref='user', lazy=True)
    
    def __init__(self, username, password, email, role='user'):
        self.username = username
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
        self.email = email
        self.role = role
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }