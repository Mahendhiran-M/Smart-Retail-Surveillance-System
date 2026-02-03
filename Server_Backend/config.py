import os

class Config:
    # --- System Settings ---
    PORT = 5000
    DEBUG = False
    
    # --- Camera Settings ---
    # 0 is usually the default webcam. Change to 1 or a video path if needed.
    CAMERA_INDEX = 1  
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    FPS = 30
    
    # --- AI Model Settings ---
    # Paths are relative to the Server_Backend directory
    YOLO_MODEL_PATH = os.path.join("models", "yolov8n.pt") 
    POSE_MODEL_PATH = os.path.join("models", "pose_model.pt") # We will add this later
    
    # Detection Thresholds
    CONFIDENCE_THRESHOLD = 0.5  # Minimum confidence to detect a person
    IOU_THRESHOLD = 0.45        # Intersection over Union for duplicate removal
    
    # --- Alert Settings ---
    ENABLE_ALERTS = True
    ALERT_COOLDOWN = 10  # Seconds between alerts to prevent spamming
    
    # WhatsApp Configuration (Demo credentials)
    # Ideally, load these from environment variables for security
    WHATSAPP_PHONE = "+919710271199"  # Target phone number for alerts
    WHATSAPP_GROUP_ID = ""            # Optional: Group ID if sending to a group
    
    # --- Storage Paths ---
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SNAPSHOT_DIR = os.path.join(BASE_DIR, "snapshots")
    LOG_DIR = os.path.join(BASE_DIR, "logs")
    RECORDING_DIR = os.path.join(BASE_DIR, "recordings")

    # Ensure directories exist
    os.makedirs(SNAPSHOT_DIR, exist_ok=True)
    os.makedirs(LOG_DIR, exist_ok=True)
    os.makedirs(RECORDING_DIR, exist_ok=True)