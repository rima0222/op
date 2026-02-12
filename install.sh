#!/bin/bash

# ۱. دریافت دسترسی روت
if [ "$EUID" -ne 0 ]; then 
  echo "لطفاً اسکریپت را با sudo اجرا کنید"
  exit
fi

echo "--- شروع نصب پنل حرفه‌ای NYR ---"

# ۲. نصب پیش‌نیازهای سیستم
apt update
apt install -y python3-pip python3-venv netcat-openbsd

# ۳. ایجاد محیط و نصب کتابخانه‌ها
mkdir -p /opt/nyr-panel
cp -r . /opt/nyr-panel
cd /opt/nyr-panel
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# ۴. تنظیم سیستم سرویس برای اجرای همیشگی پنل
cat <<EOF > /etc/systemd/system/nyr-panel.service
[Unit]
Description=NYR Professional VPN Panel
After=network.target

[Service]
User=root
WorkingDirectory=/opt/nyr-panel
ExecStart=/opt/nyr-panel/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ۵. تنظیم سرویس مانیتورینگ (Core)
cat <<EOF > /etc/systemd/system/nyr-core.service
[Unit]
Description=NYR Core Traffic Monitor
After=network.target

[Service]
User=root
WorkingDirectory=/opt/nyr-panel
ExecStart=/opt/nyr-panel/venv/bin/python core.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# ۶. فعال‌سازی سرویس‌ها
systemctl daemon-reload
systemctl enable nyr-panel nyr-core
systemctl start nyr-panel nyr-core

echo "--- نصب با موفقیت انجام شد ---"
echo "پنل شما روی پورت 6000 آماده است."
