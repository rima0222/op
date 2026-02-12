from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import subprocess
import psutil

app = Flask(__name__)

# تنظیمات
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
OVPN_FILES_PATH = "/etc/openvpn/client/"
INSTALLER_PATH = "/root/openvpn-install.sh" # مسیر پیش‌فرض اسکریپت Nyr

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    traffic_limit_gb = db.Column(db.Float, default=10.0)
    traffic_used_mb = db.Column(db.Float, default=0.0)
    expiry_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    is_online = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

# API برای ساخت کاربر جدید
@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    limit = float(data.get('limit', 10))
    days = int(data.get('days', 30))

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "این نام کاربری موجود است"}), 400

    try:
        # اجرای خودکار اسکریپت Nyr برای ساخت فایل ovpn بدون پرسش (Non-interactive)
        # 1=ساخت کاربر، username=نام کاربر
        subprocess.run(['bash', INSTALLER_PATH, '1', username], check=True, env={'MENU_OPTION': '1', 'CLIENT': username, 'PASS': '1'})
        
        new_user = User(
            username=username,
            traffic_limit_gb=limit,
            expiry_date=datetime.now() + timedelta(days=days)
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success", "message": f"کاربر {username} با موفقیت ساخته شد"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    users = User.query.all()
    online_count = User.query.filter_by(is_online=True).count()
    ram = psutil.virtual_memory().percent
    return jsonify({
        "total_users": len(users),
        "online_users": online_count,
        "ram_usage": f"{ram}%",
        "users_list": [
            {
                "username": u.username,
                "usage": f"{round(u.traffic_used_mb / 1024, 2)} / {u.traffic_limit_gb} GB",
                "expiry": (u.expiry_date - datetime.now()).days if u.expiry_date > datetime.now() else 0,
                "status": "Online" if u.is_online else "Offline"
            } for u in users
        ]
    })

@app.route('/api/download/<username>')
def download_config(username):
    return send_from_directory(OVPN_FILES_PATH, f"{username}.ovpn", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
