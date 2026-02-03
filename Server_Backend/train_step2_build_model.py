import numpy as np
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import TensorBoard

# --- CONFIG ---
DATA_PATH = os.path.join('MP_Data') 
actions = np.array(['normal', 'phone', 'theft']) # MUST match Step 1
sequence_length = 30

label_map = {label:num for num, label in enumerate(actions)}

sequences, labels = [], []

print("⏳ Loading Data...")
for action in actions:
    for sequence in range(30): # 30 videos per action
        window = []
        for frame_num in range(sequence_length):
            res = np.load(os.path.join(DATA_PATH, action, str(sequence), "{}.npy".format(frame_num)))
            window.append(res)
        sequences.append(window)
        labels.append(label_map[action])

X = np.array(sequences)
y = to_categorical(labels).astype(int)

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.05)

# --- BUILD LSTM MODEL ---
model = Sequential()
# 1. First LSTM Layer
model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(30, 132)))
# 2. Second LSTM Layer
model.add(LSTM(128, return_sequences=True, activation='relu'))
# 3. Third LSTM Layer (No return_sequences because next is Dense)
model.add(LSTM(64, return_sequences=False, activation='relu'))
# 4. Dense Layers
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
# 5. Output Layer (3 neurons for 3 actions)
model.add(Dense(actions.shape[0], activation='softmax'))

# Compile
model.compile(optimizer='Adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])

# Train
print("🧠 Training Model (This may take 5 minutes)...")
model.fit(X_train, y_train, epochs=150) # Increased epochs for better accuracy

# Save
model.save('action.h5')
print("✅ Model saved as 'action.h5'")