import cv2
import numpy as np
import os
import mediapipe as mp

# --- CONFIGURATION ---
DATA_PATH = os.path.join('MP_Data')  # Folder where data will be saved
actions = np.array(['normal', 'phone', 'theft']) # The 3 actions we want to detect
no_sequences = 30   # Record 30 videos per action
sequence_length = 30 # Each video is 30 frames long (1 second)

# Setup MediaPipe
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# Create folders
for action in actions:
    for sequence in range(no_sequences):
        try:
            os.makedirs(os.path.join(DATA_PATH, action, str(sequence)))
        except:
            pass

cap = cv2.VideoCapture(0)

# Loop through actions
for action in actions:
    print(f"-------- STARTING COLLECTION FOR: {action} --------")
    print("Get ready! Press 'Enter' in the terminal to start...")
    input() # Wait for user to be ready

    # Loop through sequences (videos)
    for sequence in range(no_sequences):
        # Loop through frames (length of video)
        for frame_num in range(sequence_length):
            ret, frame = cap.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = pose.process(image)
            
            # Draw Skeleton
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            # Wait logic (Pause at start of each video)
            if frame_num == 0:
                cv2.putText(frame, 'STARTING COLLECTION', (120,200), 
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255, 0), 4, cv2.LINE_AA)
                cv2.putText(frame, f'Collecting {action} Video #{sequence}', (15,12), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.imshow('OpenCV Feed', frame)
                cv2.waitKey(1000) # 1 second pause between clips
            else: 
                cv2.putText(frame, f'Recording {action}... {frame_num}', (15,12), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1, cv2.LINE_AA)
                cv2.imshow('OpenCV Feed', frame)

            # Export Keypoints
            if results.pose_landmarks:
                # Extract Pose landmarks
                pose_row = np.array([[res.x, res.y, res.z, res.visibility] for res in results.pose_landmarks.landmark]).flatten()
                
                # We only use Pose data (132 values)
                keypoints = pose_row 
                
                # Save as .npy file
                npy_path = os.path.join(DATA_PATH, action, str(sequence), str(frame_num))
                np.save(npy_path, keypoints)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

cap.release()
cv2.destroyAllWindows()