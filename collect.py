import cv2
import os

# Path to save the dataset
dataset_path = 'dataset'

# Create the dataset directory if it doesn't exist
if not os.path.exists(dataset_path):
    os.makedirs(dataset_path)

# Load the pre-trained Haar Cascade classifier for face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Initialize webcam
cap = cv2.VideoCapture(0)

# Ask for user ID and name
user_id = input("Enter user ID (numeric): ")
user_name = input("Enter user Name: ")

# Create a directory for the user
user_dir = os.path.join(dataset_path, f"{user_id}_{user_name}")
if not os.path.exists(user_dir):
    os.makedirs(user_dir)

print("Starting data collection. Press 'q' to quit.")

count = 0
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    for (x, y, w, h) in faces:
        # Increment image count
        count += 1
        # Crop the face region
        face_img = gray[y:y+h, x:x+w]
        # Resize the face image to a fixed size (e.g., 200x200)
        face_img = cv2.resize(face_img, (200, 200))
        # Save the image in the user directory
        cv2.imwrite(os.path.join(user_dir, f"{count}.jpg"), face_img)
        # Draw rectangle around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        cv2.putText(frame, f"Image {count}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)

    cv2.imshow('Data Collection', frame)

    # Collect 20 images then exit
    if count >= 20:
        print("Collected 20 images.")
        break

    # Press 'q' to quit early
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
