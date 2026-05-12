import numpy as np
import math
from collections import deque

class FeatureExtractor:
    def __init__(self, frame_width=1080, frame_height=1920):
        # Issue 1: Normalization Baselines
        self.frame_diagonal = math.sqrt(frame_width**2 + frame_height**2)
        
        # Issue 2: Temporal Concealment Tracking
        self.history_len = 5
        self.product_history = {} # track_id -> deque(bools)
        self.conceal_persistence = {} # track_id -> int (frames)
        
        # Issue 3: Exit-Without-Return ROIs (Adjust these to your camera view)
        # Format: (x_min, y_min, x_max, y_max)
        self.shelf_roi = (100, 200, 500, 800) 
        self.exit_roi = (800, 0, 1080, 1920)
        self.possession_state = {} # track_id -> bool

    def calculate_angle(self, a, b, c):
        """Calculates normalized angle between three points (Shoulder, Hip, Knee)"""
        a = np.array(a) # First point
        b = np.array(b) # Mid point
        c = np.array(c) # End point
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return min(angle / 180.0, 1.0) # Normalize to [0,1]

    def _in_roi(self, point, roi):
        """Checks if a centroid (x,y) is inside an ROI box"""
        return roi[0] <= point[0] <= roi[2] and roi[1] <= point[1] <= roi[3]

    def extract_features(self, track_id, person_kpts, product_bbox, prev_centroid, current_centroid, time_near_shelf):
        # Initialize state for newly tracked people
        if track_id not in self.product_history:
            self.product_history[track_id] = deque(maxlen=self.history_len)
            self.conceal_persistence[track_id] = 0
            self.possession_state[track_id] = False

        # --- 1. Normalized Distance ---
        d_hand = 1.0 # Default max
        if person_kpts and product_bbox:
            wrist = np.array(person_kpts['wrist'])
            prod_center = np.array(product_bbox)
            d_hand = np.linalg.norm(wrist - prod_center) / self.frame_diagonal
            d_hand = min(d_hand, 1.0) # Cap at 1.0

        # --- 2. Normalized Bend Angle ---
        bend_angle = 1.0 # Default straight posture
        if person_kpts and 'shoulder' in person_kpts and 'hip' in person_kpts and 'knee' in person_kpts:
            bend_angle = self.calculate_angle(
                person_kpts['shoulder'], 
                person_kpts['hip'], 
                person_kpts['knee']
            )

        # --- 3. Normalized Dwell Time ---
        dwell_time = min(time_near_shelf / 15.0, 1.0)

        # --- 4. Temporal Concealment Logic ---
        is_product_visible = product_bbox is not None
        self.product_history[track_id].append(is_product_visible)
        
        conceal_flag = 0.0
        if person_kpts:
            wrist_y = person_kpts['wrist'][1]
            hip_y = person_kpts['hip'][1]
            near_pocket = abs(wrist_y - hip_y) < 100 # Pixel proximity
            
            # Logic: Was visible for majority of past 5 frames, now gone, hand near pocket
            was_visible_recently = sum(list(self.product_history[track_id])[:-1]) >= 3
            now_gone = not is_product_visible
            
            if was_visible_recently and now_gone and near_pocket:
                self.conceal_persistence[track_id] += 1
            else:
                self.conceal_persistence[track_id] = max(0, self.conceal_persistence[track_id] - 1)
                
            # Must persist for 3 frames to trigger flag
            if self.conceal_persistence[track_id] >= 3: 
                conceal_flag = 1.0

        # --- 5. Normalized Velocity ---
        velocity = 0.0
        if prev_centroid and current_centroid:
            dist = np.linalg.norm(np.array(current_centroid) - np.array(prev_centroid))
            velocity = min(dist / self.frame_diagonal, 1.0)

        # --- 6. Exit-Without-Return Logic ---
        exit_flag = 0.0
        if current_centroid:
            # Picked up object (in shelf zone + close to hand + visible)
            if self._in_roi(current_centroid, self.shelf_roi) and is_product_visible and d_hand < 0.1:
                self.possession_state[track_id] = True
            
            # Returned object (in shelf zone + product detached/missing)
            if self._in_roi(current_centroid, self.shelf_roi) and not is_product_visible:
                self.possession_state[track_id] = False
                
            # Exiting store while still in possession
            if self._in_roi(current_centroid, self.exit_roi) and self.possession_state[track_id]:
                exit_flag = 1.0

        # Final Feature Vector: F(t) ∈ [0,1]^6
        return [d_hand, bend_angle, dwell_time, conceal_flag, velocity, exit_flag]