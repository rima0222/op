#!/bin/bash

echo "🚀 Starting Full Auto-Installation..."

# 1. نصب پیش‌نیازهای سیستم
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip wget curl ufw

# 2. دانلود اسکریپت OpenVPN نسخه Legacy (سازگار با همه ورژن‌ها)
wget https://raw.githubusercontent.com/Nyr/openvpn-install/087961f74880560731553c6598379417f7c16c02/openvpn-install.sh -O /root/openvpn-install.sh
chmod +x /root/openvpn-install.sh

# 3. نصب خودکار OpenVPN با تنظیمات پیش‌فرض
export MENU_OPTION="1"
export PROTOCOL="1"
export PORT="1194"
export DNS="1"
export CLIENT="server-admin"
bash /root/openvpn-install.sh

# 4. راه‌اندازی محیط پایتون و پنل
mkdir -p /opt/nyr-panel
cp -r . /opt/nyr-panel/
cd /opt/nyr-panel
python3 -m venv venv
./venv/bin/pip install -r requirements.txt

# 5. تنظیم فایروال
sudo ufw allow 5000/tcp
sudo ufw allow 1194/udp

# 6. ایجاد سرویس سیستم (Systemd) روی پورت 5000
cat <<EOF > /etc/systemd/system/nyr-panel.service
[Unit]
Description=NYR VPN Panel
After=network.target

[Service]
User=root
WorkingDirectory=/opt/nyr-panel
ExecStart=/opt/nyr-panel/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable nyr-panel
systemctl restart nyr-panel

echo "✅ ALL DONE!"
echo "🔗 Panel Link: http://$(curl -s ifconfig.me):5000"
