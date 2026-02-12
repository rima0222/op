# ۷. اعمال تنظیمات خودکار روی کانفیگ OpenVPN
OPENVPN_CONF="/etc/openvpn/server.conf"

if [ -f "$OPENVPN_CONF" ]; then
    echo "در حال پیکربندی خودکار فایل server.conf..."
    
    # جلوگیری از تکرار خطوط در صورت اجرای چندباره اسکریپت
    sed -i '/management 127.0.0.1 7505/d' $OPENVPN_CONF
    sed -i '/status \/var\/log\/openvpn-status.log/d' $OPENVPN_CONF
    sed -i '/status-version/d' $OPENVPN_CONF
    sed -i '/script-security/d' $OPENVPN_CONF
    sed -i '/client-connect/d' $OPENVPN_CONF

    # اضافه کردن تنظیمات جدید
    echo "management 127.0.0.1 7505" >> $OPENVPN_CONF
    echo "status /var/log/openvpn-status.log 1" >> $OPENVPN_CONF
    echo "status-version 2" >> $OPENVPN_CONF
    echo "script-security 2" >> $OPENVPN_CONF
    echo "client-connect \"/usr/bin/python3 /opt/nyr-panel/auth.py\"" >> $OPENVPN_CONF

    # ریستارت کردن OpenVPN برای اعمال تغییرات
    systemctl restart openvpn@server
else
    echo "خطا: فایل server.conf پیدا نشد. مطمئن شوید ابتدا اسکریپت Nyr را نصب کرده‌اید."
fi
