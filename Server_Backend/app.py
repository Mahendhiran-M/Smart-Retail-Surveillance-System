from flask import Flask, Response, jsonify
import cv2
from alert_engine import AlertEngine  # Importing the NEW Hybrid Engine
import threading

app = Flask(__name__)

# Initialize the Camera and the New AI Engine
camera = cv2.VideoCapture(0)  # Use 0 for Laptop Webcam
engine = AlertEngine()        # This now loads YOLOv8 + MediaPipe

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        # Pass frame through the Hybrid AI Pipeline
        # 1. YOLO Scans -> 2. MediaPipe Verifies -> 3. Draws Alerts
        processed_frame = engine.process_frame(frame)
        
        # Encode for streaming
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), 
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify({
        "status": "active", 
        "mode": "Hybrid (YOLOv8 + MediaPipe)"
    })

if __name__ == '__main__':
    # Run the server
    # host='0.0.0.0' allows the mobile app to connect
    app.run(host='0.0.0.0', port=5000, debug=False)