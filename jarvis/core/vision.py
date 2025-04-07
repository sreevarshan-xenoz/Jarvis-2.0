#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Computer Vision Module

This module provides computer vision capabilities to Jarvis,
allowing it to recognize gestures, faces, and objects.
"""

import cv2
import numpy as np
import threading
import time
from pathlib import Path
import os
import json

class VisionSystem:
    """
    Provides computer vision capabilities for multi-modal interaction.
    """
    
    def __init__(self):
        """
        Initialize the vision system.
        """
        self.camera = None
        self.is_running = False
        self.vision_thread = None
        self.frame = None
        self.last_frame_time = 0
        self.fps = 0
        
        # Advanced gesture recognition
        from core.gesture_recognition import GestureRecognizer
        self.gesture_recognizer = GestureRecognizer()
        self.gesture_cooldown = 1.0  # seconds between gesture recognitions
        self.last_gesture_time = 0
        
        # Face recognition settings
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.known_faces = {}
        self.current_user = None
        
        # 3D Holographic Animation
        from core.opengl_renderer import HolographicRenderer
        self.holographic_renderer = HolographicRenderer()
        
        # Enhanced gesture mapping
        self.gestures = {
            "wave": "Initiate conversation",
            "swipe_left": "Navigate back/previous",
            "swipe_right": "Navigate forward/next",
            "palm_open": "Stop/pause current action",
            "thumbs_up": "Confirm/accept",
            "pinch": "Zoom/scale control",
            "point": "Select/activate",
            "fist": "Grab/move objects"
        }
        
        # Callback functions for detected events
        self.callbacks = {
            "on_gesture": None,
            "on_face_detected": None,
            "on_user_recognized": None
        }
        
        # Data directory for storing face encodings
        self.data_dir = Path(os.path.dirname(os.path.dirname(__file__))) / "data" / "vision"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Load known faces if available
        self._load_known_faces()
    
    def _load_known_faces(self):
        """
        Load known face encodings from disk.
        """
        faces_file = self.data_dir / "known_faces.json"
        if faces_file.exists():
            try:
                with open(faces_file, "r") as f:
                    self.known_faces = json.load(f)
            except Exception as e:
                print(f"Error loading known faces: {e}")
    
    def _save_known_faces(self):
        """
        Save known face encodings to disk.
        """
        faces_file = self.data_dir / "known_faces.json"
        try:
            with open(faces_file, "w") as f:
                json.dump(self.known_faces, f, indent=2)
        except Exception as e:
            print(f"Error saving known faces: {e}")
    
    def start(self):
        """
        Start the vision system.
        
        Returns:
            bool: True if started successfully, False otherwise
        """
        if self.is_running:
            return True
        
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                print("Error: Could not open camera.")
                return False
            
            self.is_running = True
            self.vision_thread = threading.Thread(target=self._vision_loop, daemon=True)
            self.vision_thread.start()
            return True
        except Exception as e:
            print(f"Error starting vision system: {e}")
            return False
    
    def stop(self):
        """
        Stop the vision system.
        """
        self.is_running = False
        if self.vision_thread:
            self.vision_thread.join(timeout=1.0)
        
        if self.camera:
            self.camera.release()
            self.camera = None
    
    def _vision_loop(self):
        """
        Main vision processing loop.
        """
        frame_count = 0
        start_time = time.time()
        
        while self.is_running:
            try:
                # Capture frame
                ret, frame = self.camera.read()
                if not ret or frame is None:
                    time.sleep(0.01)
                    continue
                
                # Store the frame for external access
                self.frame = frame.copy()
                self.last_frame_time = time.time()
                
                # Calculate FPS
                frame_count += 1
                elapsed_time = time.time() - start_time
                if elapsed_time >= 1.0:
                    self.fps = frame_count / elapsed_time
                    frame_count = 0
                    start_time = time.time()
                
                # Process the frame
                self._process_frame(frame)
                
                # Small delay to reduce CPU usage
                time.sleep(0.01)
            
            except Exception as e:
                print(f"Error in vision loop: {e}")
                time.sleep(0.1)
    
    def _process_frame(self, frame):
        """
        Process a video frame for vision features.
        
        Args:
            frame: The video frame to process
        """
        # Process gestures using advanced recognition
        current_time = time.time()
        if current_time - self.last_gesture_time >= self.gesture_cooldown:
            gesture, annotated_frame = self.gesture_recognizer.process_frame(frame)
            if gesture:
                self.last_gesture_time = current_time
                if self.callbacks["on_gesture"]:
                    self.callbacks["on_gesture"](gesture.value)
                # Update holographic animation based on gesture
                self.holographic_renderer.set_state("active")
            frame = annotated_frame
        
        # Convert to grayscale for face detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        # Process detected faces
        if len(faces) > 0:
            self._process_faces(frame, faces)
            # Update holographic animation for face detection
            self.holographic_renderer.set_state("face_detected")
    
    def _process_faces(self, frame, faces):
        """
        Process detected faces for recognition.
        
        Args:
            frame: The video frame
            faces: List of detected face coordinates
        """
        # For simplicity, just process the largest face (closest to camera)
        if len(faces) > 0:
            # Find the largest face
            largest_face = max(faces, key=lambda rect: rect[2] * rect[3])
            x, y, w, h = largest_face
            
            # Extract face region
            face_img = frame[y:y+h, x:x+w]
            
            # In a real implementation, we would use face recognition here
            # For now, we'll just notify that a face was detected
            if self.callbacks["on_face_detected"]:
                self.callbacks["on_face_detected"](face_img)
    
    def _detect_gesture(self, frame):
        """
        Detect hand gestures in the frame.
        
        Args:
            frame: The video frame
            
        Returns:
            str: Detected gesture or None
        """
        # This is a placeholder for actual gesture recognition
        # In a real implementation, this would use a trained model or algorithm
        
        # For demonstration, we'll randomly detect a gesture occasionally
        if np.random.random() < 0.01:  # 1% chance of detecting a gesture
            gesture = np.random.choice(list(self.gestures.keys()))
            return gesture
        
        return None
    
    def register_callback(self, event_type, callback_function):
        """
        Register a callback function for a specific event.
        
        Args:
            event_type (str): The event type ('on_gesture', 'on_face_detected', 'on_user_recognized')
            callback_function: The function to call when the event occurs
            
        Returns:
            bool: True if registered successfully, False otherwise
        """
        if event_type in self.callbacks:
            self.callbacks[event_type] = callback_function
            return True
        return False
    
    def get_current_frame(self):
        """
        Get the most recent camera frame.
        
        Returns:
            tuple: (frame, timestamp) or (None, 0) if no frame available
        """
        if self.frame is not None:
            return (self.frame.copy(), self.last_frame_time)
        return (None, 0)
    
    def add_face(self, name, face_image):
        """
        Add a new face to the known faces database.
        
        Args:
            name (str): The name of the person
            face_image: The face image
            
        Returns:
            bool: True if added successfully, False otherwise
        """
        # In a real implementation, we would extract face encodings here
        # For now, we'll just store a placeholder
        try:
            self.known_faces[name] = {
                "added": time.time(),
                "encoding": "placeholder_encoding"
            }
            self._save_known_faces()
            return True
        except Exception as e:
            print(f"Error adding face: {e}")
            return False
    
    def remove_face(self, name):
        """
        Remove a face from the known faces database.
        
        Args:
            name (str): The name of the person
            
        Returns:
            bool: True if removed successfully, False otherwise
        """
        if name in self.known_faces:
            del self.known_faces[name]
            self._save_known_faces()
            return True
        return False
    
    def get_gesture_command_mapping(self):
        """
        Get the mapping of gestures to commands.
        
        Returns:
            dict: Mapping of gestures to commands
        """
        # This could be customized by the user
        return {
            "wave": "hello",
            "swipe_left": "previous",
            "swipe_right": "next",
            "palm_open": "stop",
            "thumbs_up": "confirm"
        }