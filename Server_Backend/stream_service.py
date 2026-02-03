import cv2
import datetime
import time
from config import Config

def generate_mjpeg_stream(camera, detector, alerter, whatsapp_service):
    """
    Generator function for Flask to stream video.
    
    Args:
        camera (CameraLogic): Instance of the camera handler.
        detector (DetectionEngine): Instance of the AI logic.
        alerter (AlertEngine): Instance of the rule-based logic.
        whatsapp_service (WhatsappAlert): Instance of the notifier.
        
    Yields:
        bytes: MJPEG encoded frame data.
    """
    while True:
        # 1. Get Frame
        frame = camera.get_frame()
        
        if frame is None:
            # If camera is warming up, yield a blank frame or skip
            time.sleep(0.1)
            continue

        # 2. Run AI Inference (Detection + Pose)
        # annotated_frame has the boxes drawn; results_data has the numbers
        annotated_frame, results_data = detector.run_inference(frame)

        # 3. Check for Alerts (The Logic)
        if results_data:
            alert_type, suspect_data = alerter.analyze_behaviors(results_data)
            
            if alert_type:
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"[ALERT] {alert_type} detected at {timestamp}!")
                
                # A. Draw Alert on Screen (Visual feedback)
                # Red text warning on the video feed
                cv2.putText(annotated_frame, f"ALERT: {alert_type}", (50, 50), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

                # B. Save Snapshot (Evidence)
                filename = f"{Config.SNAPSHOT_DIR}/alert_{int(time.time())}.jpg"
                cv2.imwrite(filename, annotated_frame)

                # C. Trigger WhatsApp (The Notification)
                whatsapp_service.send_alert(alert_type, timestamp)

        # 4. Encode for Streaming
        # Convert the processed OpenCV image (numpy array) to JPEG bytes
        (flag, encodedImage) = cv2.imencode(".jpg", annotated_frame)
        
        if not flag:
            continue

        # 5. Yield in MJPEG format (Multipart HTTP response)
        # This specific format is required for browsers/apps to see it as a video
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')