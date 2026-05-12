import cv2
from ultralytics import YOLO
import numpy as np
import os
class DetectionEngine:
    def __init__(self, model_path='yolov8n-pose.pt'):
        # Get the absolute path to the file in the current directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        local_model_path = os.path.join(current_dir, 'yolov8n-pose.pt')
        
        print(f"[INFO] Loading YOLOv8 Pose Model from: {local_model_path}")
        self.model = YOLO(local_model_path)
        
        # Tracking history: {track_id: suspicion_score}
        self.track_history = {}
        
        # Define Shelf/Theft Zone (Normalized 0-1 coordinates)
        # x1, y1, x2, y2
        self.restricted_zone = (0.2, 0.2, 0.8, 0.8) 

    def is_in_zone(self, box, frame_shape):
        """Check if person's bounding box center is in the restricted zone."""
        h, w = frame_shape[:2]
        x1, y1, x2, y2 = box
        center_x = (x1 + x2) / 2
        center_y = (y1 + y2) / 2
        
        zx1, zy1, zx2, zy2 = self.restricted_zone
        # Scale zone to pixel values
        return (zx1 * w < center_x < zx2 * w) and (zy1 * h < center_y < zy2 * h)

    def process_frame(self, frame):
        """
        Runs YOLOv8 Tracking.
        Returns: list of suspicious_candidates
        [{'id': 1, 'box': [x,y,w,h], 'keypoints': ..., 'initial_score': 50}]
        """
        # Run YOLO with built-in ByteTrack (persist=True keeps IDs across frames)
        results = self.model.track(frame, persist=True, verbose=False, tracker="bytetrack.yaml")
        
        suspicious_candidates = []
        
        if results[0].boxes and results[0].keypoints:
            boxes = results[0].boxes.xyxy.cpu().numpy()
            ids = results[0].boxes.id
            if ids is None: return [], results[0].plot() # No tracks yet
            
            ids = ids.cpu().numpy()
            keypoints = results[0].keypoints.xy.cpu().numpy() # [N, 17, 2]

            for i, track_id in enumerate(ids):
                box = boxes[i]
                kpts = keypoints[i]
                
                # Logic 1: Zone Intrusion
                in_zone = self.is_in_zone(box, frame.shape)
                
                suspicion_score = 0
                reason = "Normal"

                # Logic 2: Basic Pose Analysis (YOLO Keypoints)
                # Kpt indices: 9=L_Wrist, 10=R_Wrist, 11=L_Hip, 12=R_Hip
                # Check if wrists are near hips (Low resolution check)
                if in_zone:
                    suspicion_score += 20  # Base score for being in zone
                    
                    # Normalize simple distance check
                    # (This is rough, MediaPipe will verify it later)
                    if len(kpts) >= 13:
                        lw, rw = kpts[9], kpts[10]
                        lh, rh = kpts[11], kpts[12]
                        
                        # If wrist is close to hip (pixel distance)
                        if np.linalg.norm(lw - lh) < 60 or np.linalg.norm(rw - rh) < 60:
                            suspicion_score += 40
                            reason = "Possible Concealment"
                
                # Prepare Candidate for Stage 2 (MediaPipe) if score is high enough
                if suspicion_score > 30:
                    suspicious_candidates.append({
                        'id': int(track_id),
                        'box': box.astype(int), # [x1, y1, x2, y2]
                        'score': suspicion_score,
                        'reason': reason
                    })

        return suspicious_candidates, results[0].plot()