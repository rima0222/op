#!/bin/bash
# NYR PRO PANEL INSTALLER

if [ "$EUID" -ne 0 ]; then echo "Please run as root"; exit; fi

echo "🚀 Starting Installation..."

# نصب پیش‌نیازها
apt update && apt install -y python3-pip python3-venv netcat-openbsd

# کپی فایل‌ها و راه‌اندازی محیط
mkdir -p /opt/nyr-panel
cp -r . /opt/nyr-panel
cd /opt/nyr-panel
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# تنظیم خودکار OpenVPN server.conf
CONF="/etc/openvpn/server.conf"
if [ -f "$CONF" ]; then
    sed -i '/management/d; /status /d; /status-version/d; /script-security/d; /client-connect/d' $CONF
    echo "management 127.0.0.1 7505" >> $CONF
    echo "status /var/log/openvpn-status.log 1" >> $CONF
    echo "status-version 2" >> $CONF
    echo "script-security 2" >> $CONF
    echo "client-connect \"/usr/bin/python3 /opt/nyr-panel/auth.py\"" >> $CONF
    systemctl restart openvpn@server
fi

# اجازه دسترسی به پوشه کلاینت‌ها برای دانلود
chmod 755 /etc/openvpn/client

# ایجاد سرویس‌های سیستم (Panel & Core)
# ... (کد سرویس‌ها مشابه قبل است) ...

systemctl daemon-reload
systemctl enable nyr-panel nyr-core
systemctl start nyr-panel nyr-core

echo "✅ Done! Panel: http://YOUR_IP:6000"
