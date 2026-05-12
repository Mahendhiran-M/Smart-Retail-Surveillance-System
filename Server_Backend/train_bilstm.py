import pandas as pd
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Dropout, Input
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical

# --- CONFIGURATION ---
DATA_FILE = "training_data.csv"
MODEL_NAME = "theft_bilstm.h5"

def train_model():
    print("Loading data from CSV...")
    try:
        df = pd.read_csv(DATA_FILE)
    except FileNotFoundError:
        print(f"[ERROR] Could not find {DATA_FILE}. Did you run data_collector.py?")
        return

    # 1. Group Data into 30-frame Sequences
    sequence_ids = df['sequence_id'].unique()
    X = []
    y = []

    # Map our text labels to numbers the neural network can understand
    label_map = {"Normal": 0, "Pocketing": 1, "Bagging": 2, "Jacket": 3}

    for seq_id in sequence_ids:
        seq_data = df[df['sequence_id'] == seq_id]
        
        # Ensure the sequence is exactly 30 frames long to prevent crashes
        if len(seq_data) == 30:
            # Extract the 6 mathematical features
            features = seq_data[['d_hand', 'bend_angle', 'dwell_time', 'conceal_flag', 'velocity', 'exit_flag']].values
            X.append(features)
            
            # Grab the label for this sequence
            label_text = seq_data['theft_style'].iloc[0]
            y.append(label_map[label_text])

    # Convert lists to NumPy arrays
    X = np.array(X)
    y = np.array(y)

    print(f"Total valid 30-frame sequences found: {len(X)}")
    
    # 2. Convert labels to "One-Hot" encoding for multi-class classification
    # Example: Class 1 (Pocketing) becomes [0, 1, 0, 0]
    y_cat = to_categorical(y, num_classes=4)

    # 3. Split the data (80% for training, 20% for testing)
    X_train, X_test, y_train, y_test = train_test_split(X, y_cat, test_size=0.2, random_state=42)
    print(f"Training on {len(X_train)} sequences. Testing on {len(X_test)} sequences.\n")

    # 4. Build the Bi-LSTM Architecture
    print("Building Neural Network...")
    model = Sequential([
        Input(shape=(30, 6)),  # 30 frames, 6 features
        Bidirectional(LSTM(128, return_sequences=False)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(4, activation='softmax')  # 4 Output classes (Normal, Pocketing, Bagging, Jacket)
    ])

    model.compile(optimizer='adam', 
                  loss='categorical_crossentropy', 
                  metrics=['accuracy'])

    # 5. Train the Network!
    print("Starting Training (50 Epochs)...\n")
    history = model.fit(
        X_train, y_train,
        epochs=50,
        batch_size=16,
        validation_data=(X_test, y_test)
    )

    # 6. Save the trained weights
    model.save(MODEL_NAME)
    print(f"\n[SUCCESS] Model successfully trained and saved as '{MODEL_NAME}'!")

if __name__ == "__main__":
    train_model()