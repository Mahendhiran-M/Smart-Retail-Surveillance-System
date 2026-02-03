import cv2
import mediapipe as mp
import numpy as np
import math

class GestureVerifier:
    """
    Stage 2: High-Precision Pose Verification
    Uses MediaPipe to analyze cropped ROIs of suspicious individuals.
    Only runs when YOLO triggers a preliminary suspicion.
    """
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,       # We process cropped single frames/ROIs
            model_complexity=1,           # Balanced speed/accuracy
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6
        )

    def calculate_distance(self, p1, p2):
        """Euclidean distance between two normalized landmarks."""
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    def verify_pose(self, roi_image):
        """
        Analyzes a cropped image of a person.
        Returns: confidence_score (0-100), gesture_name (str)
        """
        if roi_image is None or roi_image.size == 0:
            return 0, "No ROI"

        # Convert to RGB for MediaPipe
        rgb_roi = cv2.cvtColor(roi_image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_roi)

        if not results.pose_landmarks:
            return 0, "No Skeleton Found"

        landmarks = results.pose_landmarks.landmark

        # --- KEYPOINT INDICES (MediaPipe) ---
        # 15=Left Wrist, 16=Right Wrist
        # 23=Left Hip, 24=Right Hip
        # 11=Left Shoulder, 12=Right Shoulder
        
        # 1. Check Hand-to-Pocket (Wrist near Hip)
        # We use a relaxed threshold because pockets vary
        l_wrist_hip = self.calculate_distance(landmarks[15], landmarks[23])
        r_wrist_hip = self.calculate_distance(landmarks[16], landmarks[24])
        
        # Threshold: 0.15 is roughly 15% of the ROI height
        pocket_threshold = 0.18 
        
        if l_wrist_hip < pocket_threshold or r_wrist_hip < pocket_threshold:
            return 85, "Confirmed: Hand in Pocket"

        # 2. Check Reaching (Wrist above Shoulder)
        # Note: Y-coordinates increase downwards in images
        if landmarks[15].y < landmarks[11].y or landmarks[16].y < landmarks[12].y:
            return 60, "Confirmed: Reaching High"

        # 3. Check Crouching (Hip Y significantly lower than normal or knee angle)
        # Simple heuristic: If shoulders are vertically close to hips (bending forward)
        # This is harder on a crop, so we rely mostly on hands here.

        return 10, "Normal Pose"