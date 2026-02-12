from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import psutil

app = Flask(__name__)

# تنظیمات دیتابیس (ذخیره در فایل database.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# مدل دیتابیس برای مدیریت کاربران
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    traffic_limit_gb = db.Column(db.Float, default=10.0)
    traffic_used_mb = db.Column(db.Float, default=0.0)
    expiry_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_online = db.Column(db.Boolean, default=False)

# ایجاد جداول دیتابیس در اولین اجرا
with app.app_context():
    db.create_all()

# مسیر اصلی برای نمایش پنل گرافیکی
@app.route('/')
def index():
    return render_template('index.html')

# API برای گرفتن آمار لحظه‌ای (توسط JS در ایندکس صدا زده می‌شود)
@app.route('/api/stats')
def get_stats():
    users = User.query.all()
    online_count = User.query.filter_by(is_online=True).count()
    
    # دریافت درصد مصرف رم سرور
    ram_usage = psutil.virtual_memory().percent
    
    return jsonify({
        "total_users": len(users),
        "online_users": online_count,
        "ram_usage": f"{ram_usage}%",
        "users_list": [
            {
                "username": u.username,
                "usage": f"{round(u.traffic_used_mb / 1024, 2)} / {u.traffic_limit_gb} GB",
                "expiry": (u.expiry_date - datetime.now()).days,
                "status": "Online" if u.is_online else "Offline"
            } for u in users
        ]
    })

# اجرای برنامه روی پورت 6000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
