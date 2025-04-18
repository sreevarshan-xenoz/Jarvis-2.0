# AURA - Augmented User Response Assistant

AURA is an advanced AI assistant with a beautiful web interface and Jarvis integration capabilities.

## Features

- **Unified Input Interface** - Single input box that handles both chat messages and commands
- **Voice Support** - Text-to-speech capabilities for AI responses
- **Jarvis Integration** - Connect to Jarvis core system when available
- **Command Execution** - Run system commands directly through the interface
- **Diagnostic Tools** - Check system status and run diagnostics
- **Modern UI** - Beautiful 3D graphics and responsive design

## Getting Started

### Prerequisites

- Node.js and npm
- Python 3.8 or higher
- A Gemini API key

### Installation

1. Clone the repository
2. Install frontend dependencies:
   ```
   npm install
   ```
3. Install backend dependencies:
   ```
   pip install fastapi uvicorn pyngrok gtts google-generativeai
   ```
4. Set up your environment variables in the `.env` file:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-pro
   REACT_APP_API_URL=http://localhost:8000
   ```

### Running the Application

Start both the backend and frontend together:
```
npm run dev
```

Or run them separately:
```
npm run api     # Start the API server
npm start       # Start the React frontend
```

## Using AURA

### Unified Input System

AURA now features a single input box that intelligently handles both conversational messages and commands:

- **Regular Text**: Simply type a message and press Enter to chat with AURA
- **Commands**: Start your message with a `/` to execute a command, for example:
  - `/status` - Check system status
  - `/open youtube.com` - Open a website
  - `/volume up` - Increase system volume

### Voice Mode

Toggle voice mode to have AI responses read aloud. Each message also has an individual audio playback button.

### Jarvis Integration

When available, you can enable Jarvis integration to leverage additional capabilities from the Jarvis system.

## Troubleshooting

If you encounter issues with the application:

1. Ensure all dependencies are installed
2. Check that the API server is running correctly
3. Verify your API keys are correctly set in the `.env` file
4. Run the diagnostic tool for a system check

## License

This project is licensed under the MIT License - see the LICENSE file for details.
