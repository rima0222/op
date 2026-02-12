import sys
from models import db, User, app
from datetime import datetime

def check_access(username):
    with app.app_context():
        user = User.query.filter_by(username=username).first()
        
        if not user:
            return False
        
        # ۱. چک کردن وضعیت فعال بودن
        if not user.is_active:
            return False
            
        # ۲. چک کردن تاریخ انقضا
        if datetime.now() > user.expiry_date:
            user.is_active = False
            db.session.commit()
            return False
            
        # ۳. چک کردن حجم مصرفی
        if (user.traffic_used_mb / 1024) >= user.traffic_limit_gb:
            user.is_active = False
            db.session.commit()
            return False

        # ۴. تک کاربره کردن (Multi-Login Prevention)
        if user.is_online:
            return False # اجازه اتصال همزمان نمی‌دهد
            
        return True

if __name__ == "__main__":
    # نام کاربری که قصد اتصال دارد توسط OpenVPN ارسال می‌شود
    username = sys.argv[1] 
    if check_access(username):
        sys.exit(0) # اجازه اتصال داده شد
    else:
        sys.exit(1) # اتصال رد شد
