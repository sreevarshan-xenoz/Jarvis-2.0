#!/usr/bin/env python3
"""
Jarvis Voice Assistant - Display Module

This module handles the visual display of assistant responses.
"""

import tkinter as tk
from tkinter import scrolledtext
import threading
import queue

class DisplayWindow:
    """
    Provides a graphical user interface for displaying assistant responses.
    """
    
    def __init__(self):
        """
        Initialize the display window.
        """
        self.root = None
        self.text_area = None
        self.response_queue = queue.Queue()
        self.is_running = False
        self.window_thread = None
    
    def _create_window(self):
        """
        Create the tkinter window and widgets.
        """
        self.root = tk.Tk()
        self.root.title("Jarvis Voice Assistant")
        self.root.geometry("600x400")
        self.root.configure(bg="#2c3e50")
        
        # Create header
        header = tk.Frame(self.root, bg="#34495e")
        header.pack(fill=tk.X, padx=10, pady=10)
        
        title = tk.Label(header, text="JARVIS", font=("Arial", 18, "bold"), fg="#ecf0f1", bg="#34495e")
        title.pack(side=tk.LEFT, padx=10)
        
        subtitle = tk.Label(header, text="Voice Assistant", font=("Arial", 12), fg="#bdc3c7", bg="#34495e")
        subtitle.pack(side=tk.LEFT, padx=5)
        
        # Create scrolled text area for responses
        frame = tk.Frame(self.root, bg="#2c3e50")
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.text_area = scrolledtext.ScrolledText(
            frame,
            wrap=tk.WORD,
            font=("Arial", 12),
            bg="#1c2833",
            fg="#ecf0f1",
            padx=10,
            pady=10
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)
        self.text_area.config(state=tk.DISABLED)
        
        # Create status bar
        status_bar = tk.Frame(self.root, bg="#34495e", height=25)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        
        status_label = tk.Label(status_bar, text="Listening...", fg="#bdc3c7", bg="#34495e")
        status_label.pack(side=tk.LEFT, padx=10)
        
        # Set up window close event
        self.root.protocol("WM_DELETE_WINDOW", self.stop)
        
        # Start checking for new responses
        self.root.after(100, self._check_queue)
    
    def _check_queue(self):
        """
        Check for new responses in the queue and update the display.
        """
        try:
            while True:
                response = self.response_queue.get_nowait()
                self._update_display(response)
                self.response_queue.task_done()
        except queue.Empty:
            pass
        
        if self.is_running:
            self.root.after(100, self._check_queue)
    
    def _update_display(self, text):
        """
        Update the text area with a new response.
        
        Args:
            text (str): The text to display
        """
        self.text_area.config(state=tk.NORMAL)
        
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.text_area.insert(tk.END, f"\n[{timestamp}] 🤖 JARVIS:\n")
        self.text_area.insert(tk.END, f"{text}\n")
        self.text_area.insert(tk.END, "\n" + "-"*50 + "\n")
        
        # Auto-scroll to the bottom
        self.text_area.see(tk.END)
        self.text_area.config(state=tk.DISABLED)
    
    def start(self):
        """
        Start the display window in a separate thread.
        """
        if not self.is_running:
            self.is_running = True
            self.window_thread = threading.Thread(target=self._run_window)
            self.window_thread.daemon = True
            self.window_thread.start()
    
    def _run_window(self):
        """
        Run the tkinter main loop in a separate thread.
        """
        self._create_window()
        self.root.mainloop()
        self.is_running = False
    
    def display(self, text):
        """
        Add a response to the display queue.
        
        Args:
            text (str): The text to display
        """
        if self.is_running:
            self.response_queue.put(text)
    
    def stop(self):
        """
        Stop the display window.
        """
        self.is_running = False
        if self.root:
            self.root.quit()
            self.root.destroy()