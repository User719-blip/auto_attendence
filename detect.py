import cv2
import numpy as np
import os
from datetime import datetime
import csv

# Absolute paths (modify as per your directory structure)
model_path = r'C:\Users\Amit Mishra\Desktop\auto_attendence\face_recognizer.yml'
dataset_path = r'C:\Users\Amit Mishra\Desktop\auto_attendence\dataset'

# Define the fixed size for face images (must match training)
fixed_size = (200, 200)  # Width x Height

# Verify model file existence
if not os.path.exists(model_path):
    raise FileNotFoundError(f"Model file not found at {model_path}")

# Initialize the LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Attempt to read the trained model
try:
    recognizer.read(model_path)
    print("Model loaded successfully.")
except cv2.error as e:
    print(f"Error loading model: {e}")
    exit(1)

# Load the Haar Cascade classifier for face detection
face_cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
if not os.path.exists(face_cascade_path):
    raise FileNotFoundError(f"Haar Cascade file not found at {face_cascade_path}")

face_cascade = cv2.CascadeClassifier(face_cascade_path)

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

# Initialize attendance dictionary to keep track of attendance
attendance = {}

# Create a mapping from label to user name
label_to_name = {}
for user_folder in os.listdir(dataset_path):
    user_path = os.path.join(dataset_path, user_folder)
    if not os.path.isdir(user_path):
        continue
    parts = user_folder.split('_')
    if len(parts) < 2:
        continue
    try:
        label = int(parts[0])
    except ValueError:
        print(f"Skipping folder {user_folder}: Cannot extract label.")
        continue
    name = '_'.join(parts[1:])  # In case name contains underscores
    label_to_name[label] = name

print("Starting real-time face recognition. Press 'q' to quit.")

# Initialize CSV with headers if not exists
csv_path = 'attendance.csv'
if not os.path.exists(csv_path):
    with open(csv_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Name', 'Timestamp'])
    print(f"Created {csv_path} with headers.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # Extract the face region
        roi_gray = gray[y:y+h, x:x+w]
        try:
            # Resize to fixed size
            roi_gray = cv2.resize(roi_gray, fixed_size)
        except cv2.error as e:
            print(f"Error resizing face region: {e}")
            continue

        # Predict the label of the face
        try:
            label, confidence = recognizer.predict(roi_gray)
        except cv2.error as e:
            print(f"Error during prediction: {e}")
            continue

        # Confidence threshold - lower values indicate better matches
        if confidence < 70:  # Adjust threshold as needed
            name = label_to_name.get(label, "Unknown")
            confidence_text = f"{round(confidence, 2)}"
            # Mark attendance if not already marked
            if name not in attendance:
                now = datetime.now()
                timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
                attendance[name] = timestamp
                # Write to CSV
                with open(csv_path, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([label, name, timestamp])
        else:
            name = "Unknown"
            confidence_text = f"{round(confidence, 2)}"

        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        # Put name and confidence
        cv2.putText(frame, str(name), (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
        cv2.putText(frame, str(confidence_text), (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

    cv2.imshow('Attendance System', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()

# Optionally, print attendance
print("Attendance:")
for name, timestamp in attendance.items():
    print(f"{name} - {timestamp}")
