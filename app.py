from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import subprocess
import psutil

app = Flask(__name__)

# Settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# مسیر دقیق فایل‌ها در اوبونتو 20.04 برای جلوگیری از خطای Not Found
OVPN_FILES_PATH = "/root"
INSTALLER_PATH = "/root/openvpn-install.sh"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    traffic_limit_gb = db.Column(db.Float, default=10.0)
    traffic_used_mb = db.Column(db.Float, default=0.0)
    expiry_date = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json
    username = data.get('username')
    limit = float(data.get('limit', 10))
    days = int(data.get('days', 30))

    if User.query.filter_by(username=username).first():
        return jsonify({"status": "error", "message": "User already exists"}), 400

    try:
        # اجرای اسکریپت نصب برای ساخت فایل ovpn
        # استفاده از تنظیمات خودکار برای جلوگیری از توقف اسکریپت
        env = os.environ.copy()
        env['MENU_OPTION'] = '1'
        env['CLIENT'] = username
        env['PASS'] = '1'
        
        subprocess.run(['bash', INSTALLER_PATH, '1', username], check=True, env=env)
        
        new_user = User(
            username=username,
            traffic_limit_gb=limit,
            expiry_date=datetime.now() + timedelta(days=days)
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/stats')
def get_stats():
    users = User.query.all()
    return jsonify({
        "total_users": len(users),
        "ram_usage": f"{psutil.virtual_memory().percent}%",
        "users_list": [
            {
                "username": u.username,
                "usage": f"{round(u.traffic_used_mb / 1024, 2)} / {u.traffic_limit_gb} GB",
                "expiry": (u.expiry_date - datetime.now()).days if u.expiry_date > datetime.now() else 0,
                "status": "Active" if u.is_active else "Inactive"
            } for u in users
        ]
    })

@app.route('/api/download/<username>')
def download_config(username):
    # این بخش فایل را مستقیماً از پوشه root برمی‌دارد تا خطای 404 ندهد
    filename = f"{username}.ovpn"
    if os.path.exists(os.path.join(OVPN_FILES_PATH, filename)):
        return send_from_directory(OVPN_FILES_PATH, filename, as_attachment=True)
    else:
        return jsonify({"status": "error", "message": "File not found on server"}), 404

if __name__ == '__main__':
    # پورت روی 5000 تنظیم شده تا مشکل Restricted Port مرورگر حل شود
    app.run(host='0.0.0.0', port=5000)
