import numpy as np
import tensorflow as tf
from collections import deque
from feature_engineering import FeatureExtractor
from risk_fusion import RiskFusion
import os

class TheftInferenceController:
    def __init__(self, model_path="theft_bilstm.h5", seq_length=30):
        self.seq_length = seq_length
        self.inference_step = 5 # Run heavy prediction every 5 frames
        
        print(f"\n[SYSTEM] Loading Bi-LSTM Model from {model_path}...")
        if os.path.exists(model_path):
            self.model = tf.keras.models.load_model(model_path)
        else:
            raise FileNotFoundError(f"Model {model_path} not found! Run train_bilstm.py first.")
            
        self.feature_extractor = FeatureExtractor()
        self.fusion_layer = RiskFusion(threshold=0.7)
        
        self.person_histories = {} 
        self.person_centroids = {}
        self.frame_counters = {}
        
        self.class_names = ["Normal", "Pocketing", "Bagging", "Jacket"]

    def update_person(self, track_id, person_kpts, product_bbox, current_centroid, time_near_shelf):
        if track_id not in self.person_histories:
            self.person_histories[track_id] = deque(maxlen=self.seq_length)
            self.person_centroids[track_id] = current_centroid
            self.frame_counters[track_id] = 0

        prev_centroid = self.person_centroids[track_id]
        self.frame_counters[track_id] += 1

        features = self.feature_extractor.extract_features(
            track_id, person_kpts, product_bbox, prev_centroid, current_centroid, time_near_shelf
        )
        
        self.person_histories[track_id].append(features)
        self.person_centroids[track_id] = current_centroid

        # Only run prediction if buffer is full AND we hit the inference step
        if len(self.person_histories[track_id]) == self.seq_length:
            if self.frame_counters[track_id] % self.inference_step == 0:
                return self._predict_theft(track_id, features)
        
        return 0.0, False, "Analyzing Sequence..." 

    def _predict_theft(self, track_id, current_features):
        sequence = np.array(self.person_histories[track_id])
        sequence = np.expand_dims(sequence, axis=0) # Reshape for LSTM: (1, 30, 6)

        # 1. Neural Network Prediction
        preds = self.model.predict(sequence, verbose=0)[0] 
        predicted_class_idx = np.argmax(preds)
        action_name = self.class_names[predicted_class_idx]
        
        # The probability of theft is the sum of Pocketing, Bagging, and Jacket probabilities
        # which is exactly 1.0 minus the 'Normal' probability
        lstm_prob = 1.0 - preds[0] 

        # 2. Risk Fusion Equation
        conceal_score = current_features[3]
        dwell_score = current_features[2] 
        exit_score = current_features[5]

        risk_score, is_theft = self.fusion_layer.compute_final_risk(
            lstm_prob, conceal_score, dwell_score, exit_score
        )

        # Safety catch: If fusion says theft but LSTM missed it
        if is_theft and predicted_class_idx == 0:
            action_name = "Suspicious Behavior"

        return risk_score, is_theft, action_name