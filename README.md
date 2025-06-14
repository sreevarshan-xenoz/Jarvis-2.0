---
title: aura-api
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 3.50.2
app_file: app.py
pinned: false
---

# AURA - Augmented User Response Assistant

AURA is an advanced AI assistant that combines multiple AI models and services to provide a comprehensive user experience. The system integrates:

- Google's Gemini API for natural language processing
- Hugging Face models for specialized tasks
- AURA Core for enhanced functionality
- Spline 3D visualization for immersive UI

## Features

- **Unified Input System**: Process both commands and conversations through a single interface
- **Voice Integration**: Text-to-speech capabilities for responses
- **3D Visualization**: Interactive Spline scenes for enhanced user experience
- **Diagnostic Tools**: Built-in system diagnostics and monitoring
- **AURA Core Integration**: Advanced AI capabilities through the AURA Core system

## Technical Details

- **Frontend**: React with styled-components and Framer Motion
- **Backend**: FastAPI with Python
- **AI Models**: Gemini API and Hugging Face models
- **3D Visualization**: Spline scenes for background and foreground elements
- **Voice**: Text-to-speech integration with audio playback

## Configuration

The system uses environment variables for configuration:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-1.5-pro-latest
HF_MODEL_NAME=your_huggingface_model
USE_HUGGINGFACE=true
```

## Development

To run the development server:

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python api_server.py
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.



note this is still in alpha version 