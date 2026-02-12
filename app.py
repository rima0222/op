from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os, subprocess, psutil

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# مسیر فایل‌ها در اوبونتو 20.04
OVPN_FILES_PATH = "/root"
INSTALLER_PATH = "/root/openvpn-install.sh"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    traffic_limit_gb = db.Column(db.Float, default=10.0)
    traffic_used_mb = db.Column(db.Float, default=0.0)
    expiry_date = db.Column(db.DateTime, nullable=False)
    initial_days = db.Column(db.Integer, default=30) # ذخیره برای ریست

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
    
    try:
        # ساخت کاربر با متغیرهای محیطی برای اتوماسیون
        os.environ['MENU_OPTION'] = '1'
        os.environ['CLIENT'] = username
        os.environ['PASS'] = '1'
        subprocess.run(['bash', INSTALLER_PATH], check=True)
        
        new_user = User(username=username, traffic_limit_gb=limit, 
                        expiry_date=datetime.now() + timedelta(days=days),
                        initial_days=days)
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/delete_user/<username>', methods=['DELETE'])
def delete_user(username):
    try:
        # حذف از سیستم OpenVPN
        os.environ['MENU_OPTION'] = '2'
        os.environ['CLIENT'] = username
        subprocess.run(['bash', INSTALLER_PATH], check=True)
        
        user = User.query.filter_by(username=username).first()
        if user:
            db.session.delete(user)
            db.session.commit()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/reset_user/<username>', methods=['POST'])
def reset_user(username):
    user = User.query.filter_by(username=username).first()
    if user:
        # ریست حجم و تمدید زمان به مقدار اولیه
        user.traffic_used_mb = 0.0
        user.expiry_date = datetime.now() + timedelta(days=user.initial_days)
        db.session.commit()
        return jsonify({"status": "success"})
    return jsonify({"status": "error", "message": "User not found"}), 404

@app.route('/api/download/<username>')
def download_config(username):
    return send_from_directory(OVPN_FILES_PATH, f"{username}.ovpn", as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
