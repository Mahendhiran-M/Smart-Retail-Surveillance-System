import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Bidirectional, Dense, Dropout, Input

def build_bilstm_model(sequence_length=30, num_features=6):
    model = Sequential([
        Input(shape=(sequence_length, num_features)),
        Bidirectional(LSTM(128, return_sequences=False)),
        Dropout(0.3),
        Dense(64, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    
    model.compile(optimizer='adam', 
                  loss='binary_crossentropy', 
                  metrics=['accuracy'])
    return model

# Run this file once to generate a blank model to test with
if __name__ == "__main__":
    model = build_bilstm_model()
    model.summary()
    # model.save('weights/bilstm_theft_model.h5')