from flask import Flask, jsonify, request
from models import db, User
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_MODEL'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ایجاد دیتابیس در اولین اجرا
with app.app_context():
    db.create_all()

@app.route('/api/add_user', methods=['POST'])
def add_user():
    data = request.json
    new_user = User(
        username=data['username'],
        password=data['password'],
        traffic_limit_gb=data['limit'],
        expiry_date=datetime.now() + timedelta(days=data['days']),
        is_active=True
    )
    # در اینجا باید اسکریپت nyr صدا زده شود تا فایل .ovpn ساخته شود
    # os.system(f"bash /root/openvpn-install.sh ...")
    
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"status": "success", "message": f"User {data['username']} created."})

@app.route('/api/stats')
def get_stats():
    # بازگرداندن آمار کلی برای داشبورد گرافیکی
    total_users = User.query.count()
    online_users = User.query.filter_by(is_online=True).count()
    return jsonify({
        "total": total_users,
        "online": online_users,
        "server_load": os.getloadavg()[0]
    })

if __name__ == '__main__':
    # اجرا روی پورت ۶۰۰۰ طبق درخواست شما
    app.run(host='0.0.0.0', port=6000, debug=True)
