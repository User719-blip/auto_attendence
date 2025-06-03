# Automated Face Recognition Attendance System

This project is a desktop application for automated attendance using face recognition. It allows you to capture face images, train a recognition model, and mark attendance automatically when a registered face is detected via webcam.

## Features

- **Face Data Collection:** Capture 20 face images per user, stored in a dedicated subfolder (`dataset/{id}_{name}`).
- **Model Training:** Train an LBPH face recognizer on the collected dataset.
- **Real-Time Detection:** Recognize faces in real-time and mark attendance.
- **Attendance Management:** View, search, export, and clear attendance records.
- **User-Friendly GUI:** Built with Tkinter for ease of use.

## Folder Structure

```
auto_attendence/
│
├── dataset/           # Contains subfolders for each user with their face images
│     └── 1_aryan/
│         ├── User.1.0.jpg
│         └── ...
├── trainer/           # Stores the trained model (trainer.yml)
├── attendance.csv     # Attendance records
├── face.py            # Main application script
├── README.md          # Project documentation
└── requirements.txt   # Python dependencies
```

## How to Use

1. **Install Requirements**
   ```
   pip install -r requirements.txt
   ```

2. **Run the Application**
   ```
   python face.py
   ```

3. **Collect Data**
   - Enter User ID and Name.
   - Click "Capture Images" to collect 20 images for the user.

4. **Train Model**
   - Click "Train Model" after collecting data for all users.

5. **Start Detection**
   - Click "Start Detection" to begin real-time face recognition and attendance marking.

6. **Attendance Management**
   - View, search, export, or clear attendance records from the right panel.

## Notes

- Make sure your webcam is connected and accessible.
- The first time you run the app, `attendance.csv` will be created automatically.
- Face images are stored in grayscale for training.
- Attendance is marked only once per user per day.

## Requirements

See [requirements.txt](requirements.txt) for the list of dependencies.

---


