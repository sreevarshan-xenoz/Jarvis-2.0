# Jarvis Animated UI

## Overview

The Jarvis Voice Assistant now features a futuristic animated UI inspired by Apple's Siri. The new interface includes:

- Dynamic wave/particle animations that react to voice input and output
- Color-coded visual states (idle, listening, speaking)
- Sleek, modern dark theme with glowing accents
- Smooth transitions between different assistant states
- Improved text display with styled timestamps and messages

## Features

### Animation States

The UI has three distinct visual states:

1. **Idle** - Blue pulsing animation with minimal movement
2. **Listening** - Green wave patterns that respond to voice input
3. **Speaking** - Orange/amber animations that activate when Jarvis responds

### Visual Elements

- **Central Circle**: Pulsing core that changes color based on the current state
- **Wave Visualization**: Animated waveform that responds to voice activity
- **Glow Effects**: Subtle lighting effects that enhance the futuristic feel
- **Styled Text**: Improved text formatting with color-coded elements

## Technical Implementation

The animated UI is implemented using:

- Tkinter Canvas for drawing and animation
- Mathematical wave functions for fluid motion
- Color transitions for state changes
- Threaded animation loop for smooth performance

## Requirements

The animated UI requires the following dependencies (included in requirements.txt):

- Pillow (PIL) for image processing
- NumPy for numerical operations
- Tkinter (included with Python)

## Future Enhancements

Possible future improvements:

- Audio spectrum visualization using FFT
- Particle effects for more dynamic animations
- 3D rendering options using PyOpenGL
- Customizable themes and animation styles

## Usage

The animated UI is automatically enabled when you start Jarvis. No additional configuration is required.

```
python main.py
```

The animation will automatically respond to voice commands and assistant responses.