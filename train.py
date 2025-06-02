import cv2
import os
import numpy as np

# Path to the dataset
dataset_path = 'dataset'

# Initialize lists to hold images and labels
faces = []
labels = []

# Define the fixed size for all face images
fixed_size = (200,200)  # Width x Height

# Iterate through each user's folder
for user_folder in os.listdir(dataset_path):
    user_path = os.path.join(dataset_path, user_folder)
    if not os.path.isdir(user_path):
        continue

    # Extract label (user ID) from folder name
    try:
        label = int(user_folder.split('_')[0])
    except ValueError:
        print(f"Skipping folder {user_folder}: Cannot extract label.")
        continue

    # Iterate through each image in the user's folder
    for image_name in os.listdir(user_path):
        image_path = os.path.join(user_path, image_name)
        # Read the image in grayscale
        img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            print(f"Failed to read image {image_path}. Skipping.")
            continue
        # Resize the image to the fixed size
        img = cv2.resize(img, fixed_size)
        faces.append(img)
        labels.append(label)

# Check if faces and labels are not empty
if not faces:
    raise ValueError("No face images found. Please check your dataset.")

# Convert lists to numpy arrays
faces = np.array(faces)
labels = np.array(labels)

# Initialize the LBPH face recognizer
recognizer = cv2.face.LBPHFaceRecognizer_create()

# Train the recognizer
recognizer.train(faces, labels)

# Save the trained model
model_path = 'face_recognizer.yml'
recognizer.save(model_path)

print(f"Training completed and model saved to {model_path}")
