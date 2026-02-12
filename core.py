import os
from datetime import datetime
from models import User, db

def check_and_apply_restrictions():
    """بررسی تمام کاربران و غیرفعال کردن کسانی که محدودیتشان تمام شده"""
    users = User.query.filter_by(is_active=True).all()
    now = datetime.now()
    
    for user in users:
        # ۱. چک کردن تاریخ انقضا
        if now > user.expiry_date:
            user.is_active = False
            disconnect_user(user.username)
            
        # ۲. چک کردن حجم (تبدیل مگابایت مصرفی به گیگابایت برای مقایسه)
        if (user.traffic_used_mb / 1024) >= user.traffic_limit_gb:
            user.is_active = False
            disconnect_user(user.username)
            
    db.session.commit()

def disconnect_user(username):
    """قطع اتصال کاربر از طریق دستور سیستم‌عامل"""
    # این دستور به OpenVPN فرمان می‌دهد که کاربر را بیرون بیندازد
    os.system(f"echo 'kill {username}' | nc -w 1 127.0.0.1 7505")
