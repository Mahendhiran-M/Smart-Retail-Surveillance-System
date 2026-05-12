from flask import Flask, request, jsonify, make_response, Response
from flask_cors import CORS
from auth import login_user, token_required
import cv2
import numpy as np
from ultralytics import YOLO
import mediapipe as mp
from inference_controller import TheftInferenceController

app = Flask(__name__)
CORS(app)

@app.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "POST,OPTIONS")
        return response
    return login_user()

# ==========================================
# Initialize the Hybrid AI Engine
# ==========================================
print("[SYSTEM] Booting Premium Hybrid AI Engine...")
yolo_model = YOLO("yolov8n.pt") 
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Load the Bi-LSTM brain
engine = TheftInferenceController(model_path="theft_bilstm.h5")

# --- EXPANDED CLASSES ---
# 39: bottle, 67: cell phone, 73: book
PROTECTED_CLASSES = [39, 67, 73] 
# 24: backpack, 26: handbag, 28: suitcase
CONTAINER_CLASSES = [24, 26, 28] 

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use 0 for Laptop, 1/2 for external

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
            
        h, w, _ = frame.shape
        
        # --- 1. YOLO Scans (Contextual Detection) ---
        results = yolo_model(frame, verbose=False)
        product_bbox = None
        current_centroid = None
        bag_detected = False 
        
        for box in results[0].boxes:
            cls = int(box.cls[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            if cls in PROTECTED_CLASSES and product_bbox is None:
                product_bbox = (x1, y1, x2, y2)
                current_centroid = (int((x1+x2)/2), int((y1+y2)/2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 150, 0), 2)
                cv2.putText(frame, "Target Object", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 150, 0), 2)
                
            elif cls in CONTAINER_CLASSES:
                bag_detected = True
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                cv2.putText(frame, "Container", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 255), 2)

        # --- 2. MediaPipe Verifies (Pose Estimation) ---
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = pose.process(frame_rgb)
        person_kpts = None
        
        if pose_results.pose_landmarks:
            lm = pose_results.pose_landmarks.landmark
            person_kpts = {
                'wrist': (int(lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].x * w), int(lm[mp_pose.PoseLandmark.RIGHT_WRIST.value].y * h)),
                'shoulder': (int(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x * w), int(lm[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y * h)),
                'hip': (int(lm[mp_pose.PoseLandmark.RIGHT_HIP.value].x * w), int(lm[mp_pose.PoseLandmark.RIGHT_HIP.value].y * h)),
                'knee': (int(lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].x * w), int(lm[mp_pose.PoseLandmark.RIGHT_KNEE.value].y * h))
            }
            mp.solutions.drawing_utils.draw_landmarks(frame, pose_results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        # --- 3. Bi-LSTM Prediction & Contextual Logic ---
        alert_text = "Status: Normal Browsing"
        alert_color = (0, 255, 0) # Green
        
        if person_kpts:
            risk, is_theft, action = engine.update_person(
                track_id=1, person_kpts=person_kpts, product_bbox=current_centroid, 
                current_centroid=person_kpts['shoulder'], time_near_shelf=5.0
            )
            
            # Contextual Logic Override
            if action == "Bagging" and not bag_detected:
                action = "Suspicious Reaching" 
                risk = risk * 0.5 
                is_theft = False  
            elif action == "Bagging" and bag_detected:
                risk = min(risk + 0.2, 1.0) 
                is_theft = True
            
            # Set HUD Text
            if is_theft:
                alert_text = f"🚨 THEFT DETECTED: {action} (Risk: {risk:.2f})"
                alert_color = (0, 0, 255) # Red
            elif risk > 0.3:
                alert_text = f"⚠️ Suspicious: {action} (Risk: {risk:.2f})"
                alert_color = (0, 255, 255) # Yellow

        # --- 4. THE NEW PREMIUM HUD OVERLAY ---
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 60), (20, 20, 20), -1) # Dark top bar
        alpha = 0.75 # Opacity
        cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)
        cv2.line(frame, (0, 60), (w, 60), alert_color, 2) # Colored bottom border
        
        # Shadow text for readability
        cv2.putText(frame, alert_text, (22, 37), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 0), 2)
        cv2.putText(frame, alert_text, (20, 35), cv2.FONT_HERSHEY_DUPLEX, 0.8, alert_color, 2)

        # Encode for streaming
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({"status": "active", "mode": "Sequence Mode (YOLOv8 + MediaPipe + Bi-LSTM)"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)