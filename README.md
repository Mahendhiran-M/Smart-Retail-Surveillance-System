# 🛒 Smart Retail Surveillance System (Hybrid AI)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)
![Flutter](https://img.shields.io/badge/Flutter-3.0%2B-02569B?logo=flutter&logoColor=white)
![AI](https://img.shields.io/badge/AI-YOLOv8%20%2B%20MediaPipe-orange)
![Status](https://img.shields.io/badge/Status-Prototype-green)

A real-time **AI-powered anti-theft system** designed for retail environments. This project utilizes a **Hybrid AI Pipeline** (YOLOv8 + MediaPipe LSTM) to detect shoplifting behaviors (like concealing items in pockets) and sends instant alerts via **WhatsApp** to a mobile dashboard.

## 🚀 Key Features

* **🕵️‍♂️ Hybrid AI Detection:** Combines **YOLOv8** (for person tracking) and **MediaPipe Pose** (for detailed action recognition) to reduce false positives.
* **🧠 Action Recognition:** Uses a custom-trained **LSTM Neural Network** to distinguish between *normal shopping*, *phone usage*, and *suspicious concealment*.
* **📱 Real-Time Mobile App:** A Flutter-based admin dashboard to view live camera feeds and receive security alerts.
* **💬 WhatsApp Integration:** Triggers automated WhatsApp alerts with timestamps and camera IDs when theft is detected.
* **🎯 Smart Zoning:** Allows setting "High-Value Zones" (ROI) where detection sensitivity is increased.

## 🛠️ Tech Stack

### **Backend (The Brain)**
* **Language:** Python 3.9
* **Framework:** Flask (API Server)
* **AI Models:** YOLOv8-Pose (Ultralytics), MediaPipe (Google), TensorFlow/Keras (LSTM)
* **Automation:** PyWhatKit (WhatsApp Automation)

### **Frontend (The Interface)**
* **Framework:** Flutter (Dart)
* **Platform:** Android / iOS / Windows

## 📦 Installation & Setup

### 1. Clone the Repository
```bash
git clone [https://github.com/YOUR_USERNAME/Smart-Retail-Surveillance-System.git](https://github.com/YOUR_USERNAME/Smart-Retail-Surveillance-System.git)
cd Smart-Retail-Surveillance-System