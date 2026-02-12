#!/bin/bash
echo "🚀 Starting Full Auto-Installation..."

# نصب پیشنیازها
apt-get update && apt-get install -y python3-venv python3-pip wget curl ufw

# دانلود اسکریپت اصلی با لینک مستقیم و پایدار
wget https://raw.githubusercontent.com/Nyr/openvpn-install/master/openvpn-install.sh -O /root/openvpn-install.sh
chmod +x /root/openvpn-install.sh

# اصلاح فایل برای اوبونتو 20 (دور زدن چک کردن ورژن)
sed -i 's/[[ $VERSION_ID -lt 22 ]]/[[ $VERSION_ID -lt 18 ]]/g' /root/openvpn-install.sh

# نصب اولیه OpenVPN اگر نصب نیست
if [ ! -d "/etc/openvpn" ]; then
    export MENU_OPTION="1"
    export PROTOCOL="1"
    export PORT="1194"
    export DNS="1"
    export CLIENT="server-admin"
    bash /root/openvpn-install.sh
fi

# راه اندازی پنل
cd /opt/nyr-panel
python3 -m venv venv
./venv/bin/pip install flask flask-sqlalchemy psutil gunicorn
ufw allow 5000/tcp
ufw allow 1194/udp

systemctl restart nyr-panel
echo "✅ Fixed! Port 5000 is ready."
