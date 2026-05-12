import cv2
import numpy as np
import pandas as pd
import os
from collections import deque
from feature_engineering import FeatureExtractor
from ultralytics import YOLO
import mediapipe as mp

# --- CONFIGURATION ---
DATA_FILE = "training_data.csv"
SEQ_LENGTH = 30
# YOLO COCO Classes: 39=bottle, 41=cup, 67=cell phone
PROTECTED_CLASSES = [39, 41, 67] 

def init_csv():
    if not os.path.exists(DATA_FILE):
        cols = ['sequence_id', 'frame_num', 'd_hand', 'bend_angle', 'dwell_time', 
                'conceal_flag', 'velocity', 'exit_flag', 'is_theft', 'theft_style']
        pd.DataFrame(columns=cols).to_csv(DATA_FILE, index=False)

def save_sequence(sequence_buffer, is_theft, theft_style, seq_id):
    rows = [[seq_id, i] + feats + [is_theft, theft_style] for i, feats in enumerate(sequence_buffer)]
    pd.DataFrame(rows).to_csv(DATA_FILE, mode='a', header=False, index=False)
    print(f"\n[SUCCESS] Saved Sequence {seq_id} | Type: {theft_style}")

def run_collector():
    init_csv()
    extractor = FeatureExtractor()
    
    print("Loading AI Models (YOLOv8 & MediaPipe)... Please wait.")
    yolo_model = YOLO("yolov8n.pt") 
    mp_pose = mp.solutions.pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    
    # Try 1 first, if it opens the wrong camera, change it to 2 or 3
    camera = cv2.VideoCapture(1, cv2.CAP_DSHOW)
    feature_buffer = deque(maxlen=SEQ_LENGTH)
    seq_id = 0
    prev_centroid = None

    print("\n" + "="*50)
    print(" DATA COLLECTION LIVE ")
    print("="*50)
    
    while True:
        success, frame = camera.read()
        if not success: break

        h, w, _ = frame.shape
        
        # 1. YOLO Detection
        results = yolo_model(frame, verbose=False, classes=PROTECTED_CLASSES)
        product_bbox = None
        current_centroid = None
        
        for box in results[0].boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            product_bbox = (x1, y1, x2, y2)
            current_centroid = (int((x1+x2)/2), int((y1+y2)/2))
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
            break # Just track the first protected item found

        # 2. MediaPipe Pose
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pose_results = mp_pose.process(frame_rgb)
        person_kpts = None
        
        if pose_results.pose_landmarks:
            lm = pose_results.pose_landmarks.landmark
            person_kpts = {
                'wrist': (int(lm[16].x * w), int(lm[16].y * h)),       # RIGHT_WRIST
                'shoulder': (int(lm[12].x * w), int(lm[12].y * h)),    # RIGHT_SHOULDER
                'hip': (int(lm[24].x * w), int(lm[24].y * h)),         # RIGHT_HIP
                'knee': (int(lm[26].x * w), int(lm[26].y * h))         # RIGHT_KNEE
            }
            cv2.circle(frame, person_kpts['wrist'], 8, (0, 255, 0), -1)

        # 3. Feature Extraction
        if current_centroid and not prev_centroid: prev_centroid = current_centroid
        
        features = extractor.extract_features(
            track_id=1, person_kpts=person_kpts, product_bbox=current_centroid, 
            prev_centroid=prev_centroid, current_centroid=current_centroid, time_near_shelf=5.0
        )
        feature_buffer.append(features)
        prev_centroid = current_centroid

        # 4. UI Overlay
        buffer_status = len(feature_buffer)
        color = (0, 255, 0) if buffer_status == SEQ_LENGTH else (0, 0, 255)
        cv2.putText(frame, f"Frames: {buffer_status}/{SEQ_LENGTH} (Wait for 30 to save)", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, "N: Normal | P: Pocket | B: Bag | J: Jacket | Q: Quit", (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        
        cv2.imshow("Data Collector", frame)

        # 5. Keyboard Controls
        key = cv2.waitKey(1) & 0xFF
        
        if buffer_status == SEQ_LENGTH:
            if key == ord('n'):
                save_sequence(list(feature_buffer), 0, "Normal", seq_id); seq_id += 1; feature_buffer.clear()
            elif key == ord('p'):
                save_sequence(list(feature_buffer), 1, "Pocketing", seq_id); seq_id += 1; feature_buffer.clear()
            elif key == ord('b'):
                save_sequence(list(feature_buffer), 1, "Bagging", seq_id); seq_id += 1; feature_buffer.clear()
            elif key == ord('j'):
                save_sequence(list(feature_buffer), 1, "Jacket", seq_id); seq_id += 1; feature_buffer.clear()
                
        if key == ord('q'): break

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_collector()