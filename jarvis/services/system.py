#!/usr/bin/env python3
"""
Jarvis Voice Assistant - System Service Module

This module handles system control functionality like volume control and application management.
"""

import os
import platform
import subprocess
import psutil
from config.settings import VOLUME_STEP

class SystemService:
    """
    Provides system control functionality.
    """
    
    def __init__(self):
        """
        Initialize the system service.
        """
        self.system = platform.system()
    
    def volume_up(self):
        """
        Increase system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system(f"nircmd.exe changesysvolume {VOLUME_STEP}")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output volume (output volume of (get volume settings) + 10)'")
            elif self.system == "Linux":
                os.system("amixer -D pulse sset Master 10%+")
            return True
        except Exception as e:
            print(f"Error adjusting volume: {str(e)}")
            return False
    
    def volume_down(self):
        """
        Decrease system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system(f"nircmd.exe changesysvolume -{VOLUME_STEP}")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output volume (output volume of (get volume settings) - 10)'")
            elif self.system == "Linux":
                os.system("amixer -D pulse sset Master 10%-")
            return True
        except Exception as e:
            print(f"Error adjusting volume: {str(e)}")
            return False
    
    def mute(self):
        """
        Mute system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system("nircmd.exe mutesysvolume 1")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output muted true'")
            elif self.system == "Linux":
                os.system("amixer -D pulse set Master mute")
            return True
        except Exception as e:
            print(f"Error muting volume: {str(e)}")
            return False
    
    def unmute(self):
        """
        Unmute system volume.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if self.system == "Windows":
                os.system("nircmd.exe mutesysvolume 0")
            elif self.system == "Darwin":  # macOS
                os.system("osascript -e 'set volume output muted false'")
            elif self.system == "Linux":
                os.system("amixer -D pulse set Master unmute")
            return True
        except Exception as e:
            print(f"Error unmuting volume: {str(e)}")
            return False
    
    def get_running_applications(self):
        """
        Get a list of running applications.
        
        Returns:
            dict: Dictionary of running applications with process IDs
        """
        running_apps = {}
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    # Skip system processes and background services
                    if proc.info['name'].lower().endswith(('.exe', '.app')) or \
                       (self.system == "Darwin" and not proc.info['name'].startswith('com.apple')):
                        running_apps[proc.info['name'].lower()] = proc.info['pid']
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            return running_apps
        except Exception as e:
            print(f"Error getting running applications: {str(e)}")
            return {}
    
    def close_application(self, app_name):
        """
        Close a running application by name.
        
        Args:
            app_name (str): The name of the application to close
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            app_name = app_name.lower()
            
            # Special handling for browser tabs
            if app_name in ['youtube', 'facebook', 'twitter', 'instagram', 'gmail']:
                return self.close_browser_tab(app_name)
            
            running_apps = self.get_running_applications()
            
            # Check for exact matches first
            for name, pid in running_apps.items():
                if app_name == name or app_name in name:
                    if self.system == "Windows":
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                                      stdout=subprocess.DEVNULL, 
                                      stderr=subprocess.DEVNULL)
                    else:  # macOS and Linux
                        os.kill(pid, 15)  # SIGTERM
                    return True
            
            # If no exact match, try partial matches
            for name, pid in running_apps.items():
                if app_name in name:
                    if self.system == "Windows":
                        subprocess.run(["taskkill", "/F", "/PID", str(pid)], 
                                      stdout=subprocess.DEVNULL, 
                                      stderr=subprocess.DEVNULL)
                    else:  # macOS and Linux
                        os.kill(pid, 15)  # SIGTERM
                    return True
            
            return False
        except Exception as e:
            print(f"Error closing application: {str(e)}")
            return False
    
    def close_browser_tab(self, tab_name):
        """
        Close a specific browser tab by its name.
        
        Args:
            tab_name (str): The name of the tab to close (e.g., 'youtube')
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Map common website names to their likely tab titles
            tab_title_patterns = {
                'youtube': ['YouTube', 'YouTube -', 'youtube.com'],
                'facebook': ['Facebook', 'Facebook -', 'facebook.com'],
                'twitter': ['Twitter', 'X', 'Twitter -', 'X -', 'twitter.com'],
                'instagram': ['Instagram', 'Instagram -', 'instagram.com'],
                'gmail': ['Gmail', 'Gmail -', 'Inbox', 'mail.google.com']
            }
            
            # Get all running processes
            browser_processes = []
            
            # Look for common browsers
            browsers = ['chrome', 'firefox', 'msedge', 'iexplore', 'safari']
            
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    for browser in browsers:
                        if browser in proc_name:
                            browser_processes.append((proc.info['pid'], proc_name))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            if not browser_processes:
                print(f"No browser processes found for closing {tab_name}")
                return False
                
            # Import here to avoid dependency issues
            try:
                import pyautogui
                import time
            except ImportError:
                # If pyautogui is not installed, try to install it
                subprocess.run(["pip", "install", "pyautogui"], 
                              stdout=subprocess.DEVNULL, 
                              stderr=subprocess.DEVNULL)
                import pyautogui
                import time
            
            # Safety settings for pyautogui
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.5  # Add small pauses between actions
            
            # Get the search patterns for the requested tab
            search_patterns = tab_title_patterns.get(tab_name, [tab_name])
            
            # Windows-specific implementation
            if self.system == "Windows":
                # First try Chrome-specific approach for better reliability
                chrome_processes = [(pid, name) for pid, name in browser_processes if 'chrome' in name]
                if chrome_processes:
                    try:
                        # Get all Chrome windows with their titles
                        chrome_windows = []
                        powershell_cmd = """
                        Add-Type @"
                        using System;
                        using System.Runtime.InteropServices;
                        using System.Text;
                        
                        public class WindowInfo {
                            [DllImport("user32.dll")]
                            public static extern IntPtr GetForegroundWindow();
                            
                            [DllImport("user32.dll")]
                            public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);
                            
                            [DllImport("user32.dll")]
                            public static extern bool EnumWindows(EnumWindowsProc enumProc, IntPtr lParam);
                            
                            [DllImport("user32.dll")]
                            public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint lpdwProcessId);
                            
                            public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);
                            
                            public static string GetWindowTitle(IntPtr hWnd) {
                                StringBuilder sb = new StringBuilder(256);
                                GetWindowText(hWnd, sb, 256);
                                return sb.ToString();
                            }
                        }
                        "@
                        
                        $chromeProcesses = Get-Process | Where-Object {$_.ProcessName -like "*chrome*"}
                        $chromeWindows = @()
                        
                        [WindowInfo]::EnumWindows(
                            [WindowInfo+EnumWindowsProc]{
                                param($hWnd, $lParam)
                                $processId = 0
                                [void][WindowInfo]::GetWindowThreadProcessId($hWnd, [ref]$processId)
                                
                                if ($chromeProcesses.Id -contains $processId) {
                                    $title = [WindowInfo]::GetWindowTitle($hWnd)
                                    if ($title -ne "") {
                                        $chromeWindows += @{"handle"=$hWnd; "title"=$title; "pid"=$processId}
                                    }
                                }
                                return $true
                            }, [IntPtr]::Zero)
                        
                        $chromeWindows | ConvertTo-Json
                        """
                        
                        # Run the PowerShell command to get Chrome windows
                        chrome_windows_json = subprocess.check_output(
                            ["powershell", "-Command", powershell_cmd],
                            stderr=subprocess.DEVNULL
                        ).decode('utf-8', errors='ignore').strip()
                        
                        import json
                        try:
                            chrome_windows = json.loads(chrome_windows_json)
                        except json.JSONDecodeError:
                            chrome_windows = []
                        
                        # Check each Chrome window for our tab patterns
                        for window in chrome_windows:
                            window_title = window.get('title', '')
                            for pattern in search_patterns:
                                if pattern.lower() in window_title.lower():
                                    # Found the tab, activate the window and close it
                                    handle = window.get('handle')
                                    if handle:
                                        # Activate the window
                                        subprocess.run(
                                            ["powershell", "-Command", f"[void][System.Runtime.InteropServices.Marshal]::SetForegroundWindow(0x{handle:X})"],
                                            stdout=subprocess.DEVNULL,
                                            stderr=subprocess.DEVNULL
                                        )
                                        time.sleep(0.5)  # Wait for window to activate
                                        
                                        # Close the tab with Ctrl+W
                                        pyautogui.hotkey('ctrl', 'w')
                                        print(f"Closed Chrome tab with title containing '{pattern}'")
                                        return True
                    except Exception as e:
                        print(f"Error with Chrome-specific approach: {str(e)}")
                        # Continue to the generic approach if Chrome-specific fails
                
                # Generic approach for all browsers
                for pid, browser_name in browser_processes:
                    try:
                        # Activate the window
                        subprocess.run(["powershell", "-Command", f"(Get-Process -Id {pid}).MainWindowHandle | ForEach-Object {{ [void][System.Runtime.InteropServices.Marshal]::SetForegroundWindow($_) }}"], 
                                      stdout=subprocess.DEVNULL, 
                                      stderr=subprocess.DEVNULL)
                        
                        time.sleep(0.5)  # Wait for window to activate
                        
                        # First try to find the tab by cycling through tabs
                        max_tabs = 15  # Reasonable limit to prevent infinite loop
                        
                        for _ in range(max_tabs):
                            # Get window title using Windows API (more reliable)
                            window_title = ""
                            try:
                                window_title = subprocess.check_output(
                                    ["powershell", "-Command", "(Get-Process | Where-Object {$_.MainWindowTitle -ne ''} | Select-Object MainWindowTitle)[0].MainWindowTitle"],
                                    stderr=subprocess.DEVNULL
                                ).decode('utf-8', errors='ignore').strip()
                            except:
                                pass
                                
                            # Check if any of our patterns match the window title
                            for pattern in search_patterns:
                                if pattern.lower() in window_title.lower():
                                    # Found the tab, close it
                                    pyautogui.hotkey('ctrl', 'w')
                                    print(f"Closed tab with title containing '{pattern}'")
                                    time.sleep(0.5)  # Give time for tab to close
                                    return True
                            
                            # Move to next tab
                            pyautogui.hotkey('ctrl', 'tab')
                            time.sleep(0.3)  # Wait for tab switch
                        
                        # If we get here, we didn't find the tab in this browser window
                        continue
                        
                    except Exception as e:
                        print(f"Error while trying to close tab in {browser_name}: {str(e)}")
                        continue
            
            # If we get here, we couldn't find the tab in any browser
            print(f"Could not find a tab containing '{tab_name}'")
            return False
            
        except Exception as e:
            print(f"Error closing browser tab: {str(e)}")
            return False