from datetime import datetime
from app import db

class AnalysisReport(db.Model):
    __tablename__ = 'analysis_report'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    log_id = db.Column(db.String(255), nullable=False)  # MongoDB日志ID
    analysis_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    result_summary = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), nullable=False)  # success/failure
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'log_id': self.log_id,
            'analysis_time': self.analysis_time.isoformat(),
            'result_summary': self.result_summary,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'user': self.user.to_dict() if self.user else None
        }