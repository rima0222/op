from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    
    # محدودیت‌ها
    traffic_limit_gb = db.Column(db.Float, default=10.0) # محدودیت کل
    traffic_used_mb = db.Column(db.Float, default=0.0)   # مصرف شده
    expiry_date = db.Column(db.DateTime, nullable=False) # تاریخ انقضا
    
    # وضعیت‌ها
    is_active = db.Column(db.Boolean, default=True)
    is_online = db.Column(db.Boolean, default=False)
    last_ip = db.Column(db.String(20))
    
    def __repr__(self):
        return f'<User {self.username}>'
