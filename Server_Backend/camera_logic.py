import cv2
import threading
import time
from config import Config

class CameraLogic:
    def __init__(self):
        self.frame = None
        self.running = False
        self.lock = threading.Lock()
        self.cap = None
        
        # Initialize camera source
        self.start_camera_stream()

    def start_camera_stream(self):
        """Attempts to open the configured camera. Falls back to default if failed."""
        print(f"[INFO] Attempting to open camera at index: {Config.CAMERA_INDEX}...")
        self.cap = cv2.VideoCapture(Config.CAMERA_INDEX)
        
        # Fallback Logic: If primary camera fails, try built-in (Index 0)
        if not self.cap.isOpened():
            print(f"[WARNING] Primary camera {Config.CAMERA_INDEX} failed.")
            print("[INFO] Attempting fallback to built-in webcam (Index 0)...")
            self.cap = cv2.VideoCapture(0)
            
        if not self.cap.isOpened():
            print("[ERROR] Could not open any camera source.")
            raise RuntimeError("No camera found.")

        # Apply Config settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, Config.FRAME_WIDTH)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
        self.cap.set(cv2.CAP_PROP_FPS, Config.FPS)
        
        # Start the capture thread
        self.running = True
        self.thread = threading.Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()
        print("[INFO] Camera service started successfully.")

    def update(self):
        """Background thread loop to read frames from the camera."""
        while self.running:
            if self.cap.isOpened():
                success, frame = self.cap.read()
                if success:
                    # Resize to ensure consistent processing speed
                    frame = cv2.resize(frame, (Config.FRAME_WIDTH, Config.FRAME_HEIGHT))
                    
                    # Thread-safe update
                    with self.lock:
                        self.frame = frame
                else:
                    print("[WARNING] Failed to read frame. Retrying...")
                    time.sleep(0.5) # Prevent CPU spike on failure
            else:
                break
            
            # Control frame rate slightly to save CPU
            time.sleep(1 / (Config.FPS + 5)) 

    def get_frame(self):
        """Returns the latest frame to the main app."""
        with self.lock:
            return self.frame.copy() if self.frame is not None else None

    def stop(self):
        """Releases the camera resource."""
        self.running = False
        if self.cap:
            self.cap.release()