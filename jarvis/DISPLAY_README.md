# Jarvis Animated Display

## Dependencies

The Jarvis animated display requires the following Python packages:

- **Pillow (PIL)**: Used for image processing and effects
- **NumPy**: Used for array operations and calculations

These dependencies have been added to the `jarvis/requirements.txt` file. You can install all required dependencies by running:

```
pip install -r jarvis/requirements.txt
```

## Troubleshooting

If you're experiencing issues with the animated display, try the following solutions:

### 1. Install Dependencies

Make sure you have all required dependencies installed:

```
pip install Pillow numpy
```

### 2. Use Basic Display Mode

If you're still having issues with the animated display, you can force Jarvis to use a basic display by running:

```
python jarvis/main.py --basic-display
```

Or in headless mode:

```
python jarvis/main.py --headless
```

### 3. Check Tkinter Support

The animated display uses Tkinter for its GUI. Ensure that Tkinter is properly installed with your Python installation.

On Windows, Tkinter is typically included with Python. On Linux, you might need to install it separately:

```
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

### 4. Debugging

If you're still experiencing issues, you can enable debug logs by setting the `JARVIS_DEBUG` environment variable:

```
# Windows
set JARVIS_DEBUG=1
python jarvis/main.py

# Linux/macOS
JARVIS_DEBUG=1 python jarvis/main.py
```

## Recent Improvements

We've made several improvements to the display module:

1. Added graceful fallback to simpler animations when dependencies are missing
2. Improved error handling throughout the animation code
3. Added better logging for troubleshooting
4. Fixed color handling and animation issues

## Contributing

If you encounter display issues not covered here, please submit a bug report with the following information:

1. Your operating system and version
2. Your Python version
3. The output of `pip list`
4. Any error messages in the console
5. Steps to reproduce the issue 