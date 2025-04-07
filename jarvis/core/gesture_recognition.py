#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Advanced Gesture Recognition Module

This module provides advanced gesture recognition capabilities using MediaPipe
for accurate hand tracking and gesture detection.
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

class GestureType(Enum):
    """Supported gesture types"""
    WAVE = "wave"
    SWIPE_LEFT = "swipe_left"
    SWIPE_RIGHT = "swipe_right"
    PALM_OPEN = "palm_open"
    THUMBS_UP = "thumbs_up"
    PINCH = "pinch"
    POINT = "point"
    FIST = "fist"

@dataclass
class HandLandmark:
    """Store hand landmark coordinates"""
    x: float
    y: float
    z: float

class GestureRecognizer:
    """Advanced gesture recognition using MediaPipe"""
    
    def __init__(self):
        """Initialize the gesture recognizer"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Gesture history for temporal analysis
        self.gesture_history: List[Tuple[GestureType, float]] = []
        self.history_size = 30  # frames
        
        # Gesture detection parameters
        self.palm_threshold = 0.2
        self.swipe_threshold = 0.3
        self.wave_threshold = 0.25
        
    def process_frame(self, frame: np.ndarray) -> Tuple[Optional[GestureType], np.ndarray]:
        """Process a video frame and detect gestures
        
        Args:
            frame: Input video frame
            
        Returns:
            Tuple of (detected gesture, annotated frame)
        """
        # Convert to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)
        
        # Draw hand landmarks
        annotated_frame = frame.copy()
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    annotated_frame,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS
                )
                
                # Convert landmarks to our format
                landmarks = self._extract_landmarks(hand_landmarks)
                
                # Detect gesture
                gesture = self._detect_gesture(landmarks)
                if gesture:
                    self.gesture_history.append((gesture, time.time()))
                    # Keep history size limited
                    if len(self.gesture_history) > self.history_size:
                        self.gesture_history.pop(0)
                    return gesture, annotated_frame
        
        return None, annotated_frame
    
    def _extract_landmarks(self, hand_landmarks) -> Dict[int, HandLandmark]:
        """Extract landmarks from MediaPipe format"""
        landmarks = {}
        for idx, landmark in enumerate(hand_landmarks.landmark):
            landmarks[idx] = HandLandmark(landmark.x, landmark.y, landmark.z)
        return landmarks
    
    def _detect_gesture(self, landmarks: Dict[int, HandLandmark]) -> Optional[GestureType]:
        """Detect gesture from hand landmarks"""
        if self._is_palm_open(landmarks):
            return GestureType.PALM_OPEN
        elif self._is_thumbs_up(landmarks):
            return GestureType.THUMBS_UP
        elif self._is_swipe_left(landmarks):
            return GestureType.SWIPE_LEFT
        elif self._is_swipe_right(landmarks):
            return GestureType.SWIPE_RIGHT
        elif self._is_wave(landmarks):
            return GestureType.WAVE
        elif self._is_pinch(landmarks):
            return GestureType.PINCH
        elif self._is_point(landmarks):
            return GestureType.POINT
        elif self._is_fist(landmarks):
            return GestureType.FIST
        return None
    
    def _is_palm_open(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect open palm gesture"""
        # Check finger extensions
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        
        # Compare with palm position
        palm_pos = landmarks[0]
        
        # Check if all fingers are extended
        fingers_extended = (
            thumb_tip.y < palm_pos.y and
            index_tip.y < palm_pos.y and
            middle_tip.y < palm_pos.y and
            ring_tip.y < palm_pos.y and
            pinky_tip.y < palm_pos.y
        )
        
        return fingers_extended
    
    def _is_thumbs_up(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect thumbs up gesture"""
        thumb_tip = landmarks[4]
        thumb_base = landmarks[2]
        index_tip = landmarks[8]
        
        # Check if thumb is pointing up and other fingers are closed
        return (
            thumb_tip.y < thumb_base.y and
            index_tip.y > thumb_base.y
        )
    
    def _is_swipe_left(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect swipe left gesture"""
        palm_pos = landmarks[0]
        if len(self.gesture_history) > 5:
            prev_gesture = self.gesture_history[-5][0]
            if prev_gesture == GestureType.PALM_OPEN:
                return palm_pos.x < self.swipe_threshold
        return False
    
    def _is_swipe_right(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect swipe right gesture"""
        palm_pos = landmarks[0]
        if len(self.gesture_history) > 5:
            prev_gesture = self.gesture_history[-5][0]
            if prev_gesture == GestureType.PALM_OPEN:
                return palm_pos.x > (1 - self.swipe_threshold)
        return False
    
    def _is_wave(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect wave gesture"""
        if len(self.gesture_history) > 10:
            # Check for alternating up/down movement
            palm_positions = [landmarks[0].y for _, _ in self.gesture_history[-10:]]
            variations = np.diff(palm_positions)
            sign_changes = np.diff(np.signbit(variations)).sum()
            return sign_changes >= 4  # At least 4 direction changes
        return False
    
    def _is_pinch(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect pinch gesture"""
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        
        # Calculate distance between thumb and index finger
        distance = np.sqrt(
            (thumb_tip.x - index_tip.x)**2 +
            (thumb_tip.y - index_tip.y)**2 +
            (thumb_tip.z - index_tip.z)**2
        )
        
        return distance < 0.05  # Close proximity threshold
    
    def _is_point(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect pointing gesture"""
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        palm_pos = landmarks[0]
        
        # Check if index finger is extended while others are closed
        return (
            index_tip.y < palm_pos.y and
            middle_tip.y > palm_pos.y and
            ring_tip.y > palm_pos.y and
            pinky_tip.y > palm_pos.y
        )
    
    def _is_fist(self, landmarks: Dict[int, HandLandmark]) -> bool:
        """Detect closed fist gesture"""
        finger_tips = [landmarks[tip] for tip in [8, 12, 16, 20]]
        palm_pos = landmarks[0]
        
        # Check if all fingers are closed
        return all(tip.y > palm_pos.y for tip in finger_tips)