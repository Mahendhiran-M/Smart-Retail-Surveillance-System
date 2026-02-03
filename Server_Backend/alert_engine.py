import cv2
import time
import numpy as np
from detection_engine import DetectionEngine
from gesture_verifier import GestureVerifier
from whatsapp_alert import WhatsappAlert
from config import Config

class AlertEngine:
    def __init__(self):
        print("[INIT] Initializing Hybrid Theft Detection System...")
        self.detector = DetectionEngine()       # YOLOv8
        self.verifier = GestureVerifier()       # MediaPipe
        self.alerter = WhatsappAlert()          # WhatsApp
        
        self.last_alert_time = 0
        self.frame_skip = 2  # Process every 2nd frame to save CPU
        self.frame_count = 0

    def process_frame(self, frame):
        self.frame_count += 1
        # Skip frames for performance optimization
        if self.frame_count % self.frame_skip != 0:
            return frame

        # --- STAGE 1: GLOBAL DETECTION (YOLO) ---
        candidates, annotated_frame = self.detector.process_frame(frame)
        
        final_frame = annotated_frame
        h, w, _ = frame.shape

        # --- STAGE 2: TARGETED VERIFICATION (MediaPipe) ---
        for person in candidates:
            x1, y1, x2, y2 = person['box']
            track_id = person['id']
            yolo_score = person['score']

            # Safety check for image bounds
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)

            # Crop the "Region of Interest" (ROI)
            roi = frame[y1:y2, x1:x2]

            # Pass ROI to MediaPipe Verifier
            mp_score, mp_reason = self.verifier.verify_pose(roi)

            # --- STAGE 3: FUSION & SCORING ---
            # Weighted Average: MediaPipe (Accuracy) 70% + YOLO (Context) 30%
            final_confidence = (yolo_score * 0.3) + (mp_score * 0.7)

            # Visualization
            color = (0, 255, 255) # Yellow (Warning)
            status = f"ID:{track_id} | Risk: {int(final_confidence)}%"
            
            if final_confidence > 75:
                color = (0, 0, 255) # Red (Danger)
                status = f"ID:{track_id} | THEFT DETECTED!"
                
                # Draw the specific logic detected
                cv2.putText(final_frame, f"Reason: {mp_reason}", (x1, y1 - 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
                
                # Trigger Alert
                self.trigger_alert(mp_reason, final_confidence)

            # Draw final bounding box and score
            cv2.rectangle(final_frame, (x1, y1), (x2, y2), color, 3)
            cv2.putText(final_frame, status, (x1, y1 - 10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        return final_frame

    def trigger_alert(self, reason, confidence):
        current_time = time.time()
        # 15 Seconds Cooldown between alerts
        if (current_time - self.last_alert_time) > 15:
            print(f"🚨 ALERT TRIGGERED: {reason} (Conf: {confidence}%)")
            
            timestamp = time.strftime("%Y-%m-%d %I:%M %p")
            msg_body = f"{reason} (Confidence: {int(confidence)}%)"
            
            # Send WhatsApp
            self.alerter.send_alert(msg_body, timestamp)
            
            self.last_alert_time = current_time

if __name__ == "__main__":
    # Quick Test Loop
    cap = cv2.VideoCapture(0)
    engine = AlertEngine()
    
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        processed = engine.process_frame(frame)
        cv2.imshow("Smart Retail Engine", processed)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()