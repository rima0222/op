import time
import os
from models import db, User, app
from datetime import datetime

# مسیر فایل وضعیت OpenVPN (باید در server.conf تنظیم شده باشد)
STATUS_LOG_PATH = "/var/log/openvpn-status.log"

def update_system_logic():
    with app.app_context():
        if not os.path.exists(STATUS_LOG_PATH):
            print(f"Error: {STATUS_LOG_PATH} not found!")
            return

        # ابتدا همه را آفلاین فرض می‌کنیم تا لیست جدید جایگزین شود
        User.query.update({User.is_online: False})
        
        with open(STATUS_LOG_PATH, "r") as f:
            lines = f.readlines()
            
            for line in lines:
                # جدا کردن کلاینت‌های متصل (فرمت OpenVPN Status V2)
                if line.startswith("CLIENT_LIST"):
                    parts = line.split(',')
                    if len(parts) < 5: continue
                    
                    username = parts[1]
                    bytes_received = int(parts[5]) # مقدار بایت دریافتی
                    bytes_sent = int(parts[6])     # مقدار بایت ارسالی
                    
                    # محاسبه حجم مصرفی جدید (تبدیل به مگابایت)
                    total_mb = (bytes_received + bytes_sent) / (1024 * 1024)
                    
                    user = User.query.filter_by(username=username).first()
                    if user:
                        user.is_online = True
                        # اضافه کردن مصرف جدید به مصرف قبلی
                        user.traffic_used_mb += total_mb
                        
                        # چک کردن محدودیت‌ها در لحظه
                        if (user.traffic_used_mb / 1024) >= user.traffic_limit_gb or \
                           datetime.now() > user.expiry_date:
                            user.is_active = False
                            # دستور قطع اتصال فوری از سرور
                            os.system(f"echo 'kill {username}' | nc -w 1 127.0.0.1 7505")

        db.session.commit()

if __name__ == "__main__":
    print("Core service started. Monitoring traffic and users...")
    while True:
        try:
            update_system_logic()
        except Exception as e:
            print(f"Update Error: {e}")
        
        time.sleep(30) # هر 30 ثانیه یکبار کل سیستم را چک کن
