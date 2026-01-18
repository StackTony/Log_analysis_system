from datetime import datetime
from app import db

class Case(db.Model):
    __tablename__ = 'case'
    
    id = db.Column(db.Integer, primary_key=True)
    check_item_id = db.Column(db.Integer, db.ForeignKey('check_item.id'), nullable=False)
    log_id = db.Column(db.String(255), nullable=False)  # MongoDB日志ID
    log_content = db.Column(db.Text, nullable=False)
    analysis_result = db.Column(db.Text)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending/processed
    processed_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'check_item_id': self.check_item_id,
            'log_id': self.log_id,
            'log_content': self.log_content,
            'analysis_result': self.analysis_result,
            'status': self.status,
            'processed_by': self.processed_by,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'check_item': self.check_item.to_dict() if self.check_item else None,
            'processor': self.processor.to_dict() if self.processor else None
        }