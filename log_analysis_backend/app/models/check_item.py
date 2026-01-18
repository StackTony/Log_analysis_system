from datetime import datetime
from app import db

class CheckItem(db.Model):
    __tablename__ = 'check_item'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    rule = db.Column(db.Text, nullable=False)  # 正则表达式或关键词
    rule_type = db.Column(db.String(20), nullable=False)  # regex/keyword
    severity = db.Column(db.String(20), nullable=False)  # low/medium/high/critical
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系定义
    cases = db.relationship('Case', backref='check_item', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'rule': self.rule,
            'rule_type': self.rule_type,
            'severity': self.severity,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }