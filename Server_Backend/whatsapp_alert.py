import pywhatkit
import threading
import datetime
import time
from config import Config

class WhatsappAlert:
    def __init__(self):
        self.target_phone = Config.WHATSAPP_PHONE
        self.enabled = Config.ENABLE_ALERTS
        
    def send_alert(self, alert_type, timestamp_str):
        if not self.enabled:
            print("[INFO] WhatsApp alerts are disabled.")
            return

        # Get current date
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")

        # Formatted Message
        message = (
            f"🚨 *SECURITY ALERT* 🚨\n\n"
            f"⚠️ *Type:* {alert_type}\n"
            f"📅 *Date:* {current_date}\n"
            f"🕒 *Time:* {timestamp_str}\n"
            f"📍 *Camera:* Cam-{Config.CAMERA_INDEX}\n\n"
            f"Please check the dashboard immediately!"
        )

        # Run in separate thread so video doesn't freeze
        alert_thread = threading.Thread(target=self._send_thread, args=(message,))
        alert_thread.daemon = True
        alert_thread.start()

    def _send_thread(self, message):
        """
        Sends the message using Browser Automation.
        REQUIREMENTS:
        1. Laptop screen must be ON (not sleeping).
        2. WhatsApp Web must be logged in on Chrome/Edge.
        3. Do not touch mouse/keyboard while it runs.
        """
        try:
            print(f"[INFO] ⏳ Preparing WhatsApp alert to {self.target_phone}...")
            
            # OPTIMIZED SETTINGS:
            # wait_time=20: Gives browser 20s to load (safe for slow internet)
            # tab_close=True: Closes tab after sending to save RAM
            # close_time=5: Waits 5s AFTER sending to ensure message is delivered
            
            pywhatkit.sendwhatmsg_instantly(
                phone_no=self.target_phone, 
                message=message, 
                wait_time=20,      # Increased from 15 -> 20 for safety
                tab_close=True, 
                close_time=5       # Increased from 3 -> 5 to ensure delivery
            )
            print("[SUCCESS] ✅ WhatsApp alert sent successfully!")
            
        except Exception as e:
            print(f"[ERROR] ❌ Failed to send WhatsApp alert: {e}")
            print("TIP: Make sure your screen is unlocked and browser is logged in.")