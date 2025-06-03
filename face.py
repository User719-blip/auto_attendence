import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import subprocess
import threading
import csv
from datetime import datetime
import cv2
import numpy as np
from PIL import Image, ImageTk
import time

class AttendanceSystemGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Automated Attendance System")
        self.root.geometry("1200x800")
        
        # Configuration
        self.dataset_dir = "dataset"
        self.trainer_dir = "trainer"
        self.attendance_file = "attendance.csv"
        self.cascade_path = "haarcascade_frontalface_default.xml"
        
        # Create directories if they don't exist
        os.makedirs(self.dataset_dir, exist_ok=True)
        os.makedirs(self.trainer_dir, exist_ok=True)
        
        # Initialize face recognizer
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # GUI Variables
        self.user_id_var = tk.StringVar()
        self.user_name_var = tk.StringVar()
        self.status_var = tk.StringVar(value="System Ready")
        self.camera_var = tk.BooleanVar(value=True)
        self.detection_running = False
        
        # Create main interface
        self.create_widgets()
        
        # Initialize camera
        self.cap = None
        self.init_camera()
        
        # Load attendance records
        self.initialize_attendance_file()
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Camera and operations
        left_panel = ttk.Frame(main_frame, width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)
        
        # Right panel - Attendance management
        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Camera frame
        camera_frame = ttk.LabelFrame(left_panel, text="Camera", padding="10")
        camera_frame.pack(fill=tk.BOTH, expand=True)
        
        self.camera_label = ttk.Label(camera_frame)
        self.camera_label.pack(fill=tk.BOTH, expand=True)
        
        # Collection controls
        collection_frame = ttk.LabelFrame(left_panel, text="Data Collection", padding="10")
        collection_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(collection_frame, text="User ID:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(collection_frame, textvariable=self.user_id_var).grid(row=0, column=1, sticky=tk.EW)
        
        ttk.Label(collection_frame, text="User Name:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(collection_frame, textvariable=self.user_name_var).grid(row=1, column=1, sticky=tk.EW)
        
        ttk.Button(collection_frame, text="Capture Images", command=self.start_capture).grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.EW)
        
        # Training controls
        train_frame = ttk.LabelFrame(left_panel, text="Model Training", padding="10")
        train_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(train_frame, text="Train Model", command=self.train_model).pack(fill=tk.X)
        
        # Detection controls
        detect_frame = ttk.LabelFrame(left_panel, text="Face Detection", padding="10")
        detect_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(detect_frame, text="Start Detection", command=self.start_detection).pack(side=tk.LEFT, expand=True)
        ttk.Button(detect_frame, text="Stop Detection", command=self.stop_detection).pack(side=tk.LEFT, expand=True)
        
        # Status bar
        status_frame = ttk.Frame(left_panel)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, textvariable=self.status_var).pack(side=tk.LEFT)
        
        # Attendance management
        self.attendance_tree = ttk.Treeview(right_panel, columns=('ID', 'Name', 'Timestamp'), show='headings')
        self.attendance_tree.heading('ID', text='ID')
        self.attendance_tree.heading('Name', text='Name')
        self.attendance_tree.heading('Timestamp', text='Timestamp')
        self.attendance_tree.column('ID', width=50)
        self.attendance_tree.column('Name', width=150)
        self.attendance_tree.column('Timestamp', width=200)
        
        scroll_y = ttk.Scrollbar(right_panel, orient=tk.VERTICAL, command=self.attendance_tree.yview)
        scroll_x = ttk.Scrollbar(right_panel, orient=tk.HORIZONTAL, command=self.attendance_tree.xview)
        self.attendance_tree.configure(yscroll=scroll_y.set, xscroll=scroll_x.set)
        
        self.attendance_tree.grid(row=0, column=0, sticky='nsew')
        scroll_y.grid(row=0, column=1, sticky='ns')
        scroll_x.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights
        right_panel.grid_rowconfigure(0, weight=1)
        right_panel.grid_columnconfigure(0, weight=1)
        
        # Management controls
        manage_frame = ttk.Frame(right_panel)
        manage_frame.grid(row=2, column=0, columnspan=2, sticky='ew', pady=5)
        
        ttk.Button(manage_frame, text="Refresh", command=self.load_attendance).pack(side=tk.LEFT, padx=2)
        ttk.Button(manage_frame, text="Export", command=self.export_attendance).pack(side=tk.LEFT, padx=2)
        ttk.Button(manage_frame, text="Clear", command=self.clear_attendance).pack(side=tk.LEFT, padx=2)
        
        # Search frame
        search_frame = ttk.Frame(right_panel)
        search_frame.grid(row=3, column=0, columnspan=2, sticky='ew', pady=5)
        
        self.search_var = tk.StringVar()
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2)
        ttk.Button(search_frame, text="Search", command=self.search_attendance).pack(side=tk.LEFT, padx=2)
        
        # Load initial attendance data
        self.load_attendance()
        
    def init_camera(self):
        """Initialize the camera"""
        if self.cap is not None:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Error", "Could not open camera")
            return
        
        self.update_camera()
        
    def update_camera(self):
        """Update camera feed"""
        if self.cap is None or not self.cap.isOpened():
            return
            
        ret, frame = self.cap.read()
        if ret:
            # Convert to RGB and resize
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = self.resize_with_aspect_ratio(frame, width=400)
            
            # Convert to ImageTk format
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            
            # Update label
            self.camera_label.imgtk = imgtk
            self.camera_label.configure(image=imgtk)
        
        # Schedule next update
        if self.camera_var.get():
            self.root.after(10, self.update_camera)
        
    def resize_with_aspect_ratio(self, image, width=None, height=None, inter=cv2.INTER_AREA):
        """Resize image while maintaining aspect ratio"""
        dim = None
        (h, w) = image.shape[:2]

        if width is None and height is None:
            return image

        if width is not None:
            r = width / float(w)
            dim = (width, int(h * r))
        else:
            r = height / float(h)
            dim = (int(w * r), height)

        return cv2.resize(image, dim, interpolation=inter)
        
    def start_capture(self):
        """Start capturing face images for training"""
        user_id = self.user_id_var.get().strip()
        user_name = self.user_name_var.get().strip()
        
        if not user_id or not user_name:
            messagebox.showwarning("Input Error", "Please enter both User ID and Name")
            return
            
        # Start capture in a separate thread
        threading.Thread(target=self.capture_images, args=(user_id, user_name), daemon=True).start()
        
    def capture_images(self, user_id, user_name):
        """Capture face images and save to dataset"""
        self.status_var.set(f"Capturing images for {user_name}...")
        
        face_cascade = cv2.CascadeClassifier(self.cascade_path)
        count = 0
        max_images = 20
        
        while count < max_images:
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Save the face image
                face_img = gray[y:y+h, x:x+w]
                img_path = os.path.join(self.dataset_dir, f"User.{user_id}.{count}.jpg")
                cv2.imwrite(img_path, face_img)
                
                count += 1
                self.status_var.set(f"Captured {count}/{max_images} images for {user_name}")
                
                # Display count on image
                cv2.putText(frame, str(count), (x+5, y+h-5), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                # Show the frame with rectangle
                cv2.imshow('Capturing Faces', frame)
                
                # Wait for 100ms between captures
                time.sleep(0.1)
                
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cv2.destroyAllWindows()
        self.status_var.set(f"Completed capturing {count} images for {user_name}")
        messagebox.showinfo("Complete", f"Successfully captured {count} images for {user_name}")
        
    def train_model(self):
        """Train the face recognition model"""
        self.status_var.set("Training model...")
        
        # Run training in a separate thread
        threading.Thread(target=self._train_model_thread, daemon=True).start()
        
    def _train_model_thread(self):
        """Thread function for model training"""
        try:
            # Get the training images
            image_paths = [os.path.join(self.dataset_dir, f) for f in os.listdir(self.dataset_dir)]
            
            faces = []
            ids = []
            
            for image_path in image_paths:
                if not image_path.endswith(".jpg"):
                    continue
                    
                # Convert image to grayscale
                img = Image.open(image_path).convert('L')
                img_np = np.array(img, 'uint8')
                
                # Get the user id from the image path
                id = int(os.path.split(image_path)[-1].split(".")[1])
                
                faces.append(img_np)
                ids.append(id)
                
            if not faces:
                messagebox.showwarning("Error", "No training images found in dataset folder")
                self.status_var.set("Training failed - no images")
                return
                
            # Train the model
            self.face_recognizer.train(faces, np.array(ids))
            
            # Save the model
            model_path = os.path.join(self.trainer_dir, "trainer.yml")
            self.face_recognizer.write(model_path)
            
            self.status_var.set(f"Training complete - {len(faces)} images")
            messagebox.showinfo("Success", f"Model trained successfully with {len(faces)} images")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error during training: {str(e)}")
            self.status_var.set("Training failed")
        
    def start_detection(self):
        """Start face detection and attendance marking"""
        if self.detection_running:
            return
            
        # Load the trained model
        model_path = os.path.join(self.trainer_dir, "trainer.yml")
        if not os.path.exists(model_path):
            messagebox.showwarning("Error", "No trained model found. Please train the model first.")
            return
            
        try:
            self.face_recognizer.read(model_path)
        except:
            messagebox.showwarning("Error", "Could not load trained model")
            return
            
        self.detection_running = True
        self.status_var.set("Detection running...")
        
        # Start detection in a separate thread
        threading.Thread(target=self._detect_faces, daemon=True).start()
        
    def stop_detection(self):
        """Stop face detection"""
        self.detection_running = False
        self.status_var.set("Detection stopped")
        
    def _detect_faces(self):
        """Thread function for face detection"""
        face_cascade = cv2.CascadeClassifier(self.cascade_path)
        font = cv2.FONT_HERSHEY_SIMPLEX
        
        while self.detection_running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                continue
                
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.3, 5)
            
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Try to recognize the face
                id, confidence = self.face_recognizer.predict(gray[y:y+h, x:x+w])
                
                # Check if confidence is less than 100 (0 is perfect match)
                if confidence < 100:
                    # Get user name from attendance records
                    user_name = self.get_user_name(id)
                    confidence_text = f"  {round(100 - confidence)}%"
                    
                    # Mark attendance if not already marked today
                    self.mark_attendance(id, user_name)
                else:
                    user_name = "unknown"
                    confidence_text = f"  {round(100 - confidence)}%"
                    
                cv2.putText(frame, str(user_name), (x+5, y-5), font, 1, (255, 255, 255), 2)
                cv2.putText(frame, str(confidence_text), (x+5, y+h-5), font, 1, (255, 255, 0), 1)
                
            # Display the frame
            cv2.imshow('Face Detection', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
        cv2.destroyAllWindows()
        self.detection_running = False
        
    def get_user_name(self, user_id):
        """Get user name from attendance records"""
        try:
            with open(self.attendance_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['ID']) == user_id:
                        return row['Name']
        except:
            pass
        return f"User-{user_id}"
        
    def mark_attendance(self, user_id, user_name):
        """Mark attendance for a recognized user"""
        # Check if already marked today
        today = datetime.now().strftime("%Y-%m-%d")
        already_marked = False
        
        try:
            with open(self.attendance_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if int(row['ID']) == user_id and row['Timestamp'].startswith(today):
                        already_marked = True
                        break
        except:
            pass
            
        if not already_marked:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.attendance_file, 'a', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([user_id, user_name, timestamp])
                
            # Update the attendance display
            self.root.after(0, self.load_attendance)
            self.status_var.set(f"Attendance marked for {user_name}")
        
    def initialize_attendance_file(self):
        """Initialize the attendance file with headers if it doesn't exist"""
        if not os.path.exists(self.attendance_file):
            with open(self.attendance_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', 'Name', 'Timestamp'])
                
    def load_attendance(self):
        """Load attendance records into the treeview"""
        # Clear existing data
        for item in self.attendance_tree.get_children():
            self.attendance_tree.delete(item)
            
        # Read records from CSV
        try:
            with open(self.attendance_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    self.attendance_tree.insert('', tk.END, values=(row['ID'], row['Name'], row['Timestamp']))
        except Exception as e:
            messagebox.showerror("Error", f"Could not load attendance: {str(e)}")
            
    def export_attendance(self):
        """Export attendance records to a file"""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Export Attendance"
        )
        
        if file_path:
            try:
                with open(self.attendance_file, 'r') as f_in, open(file_path, 'w', newline='') as f_out:
                    f_out.write(f_in.read())
                messagebox.showinfo("Success", f"Attendance exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export attendance: {str(e)}")
                
    def clear_attendance(self):
        """Clear all attendance records"""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all attendance records?"):
            try:
                with open(self.attendance_file, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['ID', 'Name', 'Timestamp'])
                self.load_attendance()
                messagebox.showinfo("Success", "Attendance records cleared")
            except Exception as e:
                messagebox.showerror("Error", f"Could not clear attendance: {str(e)}")
                
    def search_attendance(self):
        """Search attendance records"""
        search_term = self.search_var.get().lower()
        
        # Show all if search is empty
        if not search_term:
            for item in self.attendance_tree.get_children():
                self.attendance_tree.item(item, tags=('',))
            return
            
        # Hide non-matching items
        for item in self.attendance_tree.get_children():
            values = [str(v).lower() for v in self.attendance_tree.item(item)['values']]
            if any(search_term in v for v in values):
                self.attendance_tree.item(item, tags=('match',))
            else:
                self.attendance_tree.item(item, tags=('nomatch',))
                
        # Hide non-matching items
        self.attendance_tree.tag_configure('nomatch', foreground='gray90')
        
    def on_closing(self):
        """Handle window closing"""
        if self.cap is not None:
            self.cap.release()
        self.detection_running = False
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceSystemGUI(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
