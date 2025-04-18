# AURA (Augmented User Response Assistant)

AURA is an advanced AI assistant that combines a beautiful 3D user interface with powerful AI capabilities using Google's Gemini API. It features voice interaction, command execution, and a customizable interface.

## Features

- Beautiful 3D animated UI with layered visual effects
- AI-powered responses using Google's Gemini Pro API
- Voice interaction with text-to-speech capabilities
- Command execution for web browsing, volume control, and more
- Diagnostic tools to verify AI connectivity
- Knowledge base search using RAG (if configured)

## Setup Instructions

### 1. Frontend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/AURA.git
   cd AURA
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm start
   ```

### 2. API Server Setup

The AURA application requires a Python API server to connect to Google's Gemini API:

1. Install the required dependencies:
   ```bash
   pip install -r api_requirements.txt
   ```

2. Set up your Gemini API key (already provided in the code, but you can use your own):
   ```bash
   # Windows
   set GEMINI_API_KEY=AIzaSyDT70dXIaCcjZsB8ktCGQlbMqLnQ5PW2RU
   
   # Mac/Linux
   export GEMINI_API_KEY=AIzaSyDT70dXIaCcjZsB8ktCGQlbMqLnQ5PW2RU
   ```

3. Start the API server:
   ```bash
   python api_server.py
   ```

   The API server will be available at http://localhost:8000.

### 3. Supabase Edge Functions (Optional - for full deployment)

After setting up the Python API server, you can deploy the Supabase Edge Functions:

1. Install the Supabase CLI:
   ```bash
   npm install -g supabase
   ```

2. Log in to Supabase:
   ```bash
   supabase login
   ```

3. Link your project:
   ```bash
   supabase link --project-ref yrut1xveshjsmwutdgwv
   ```

4. Deploy the Edge Functions:
   ```bash
   supabase functions deploy
   ```

5. Set up environment variables in the Supabase Dashboard:
   - Go to your Supabase project dashboard
   - Navigate to Settings → API → Edge Functions
   - Add the following environment variables:
     - `GEMINI_API_KEY`: Your Google Gemini API key
     - `GEMINI_API_URL`: URL of your chat endpoint (e.g., "http://localhost:8000/chat")
     - `COMMAND_API_URL`: URL of your command endpoint (e.g., "http://localhost:8000/execute")
     - `STATUS_API_URL`: URL of your status endpoint (e.g., "http://localhost:8000/status")
     - `TTS_API_URL`: URL of your TTS endpoint (e.g., "http://localhost:8000/tts")

   If your Python API server is running locally, you'll need to expose it to the internet for Supabase Edge Functions to access it. You can use a service like ngrok:

   ```bash
   npx ngrok http 8000
   ```

   Then use the ngrok URL as the base for your API endpoints in the Supabase environment variables.

## Using AURA

### Available Commands

AURA supports various commands that you can type in the command bar:

- **Web Browsing**:
  - `open google.com` - Open a website in your default browser
  - `go to youtube.com` - Navigate to a specific website

- **Volume Control**:
  - `volume up` - Increase system volume
  - `volume down` - Decrease system volume
  - `mute` - Mute system audio
  - `unmute` - Unmute system audio
  - `volume set 50` - Set volume to a specific level (works on Mac/Linux)

- **System Commands**:
  - `status` - Check the AI model status
  - `help` - Show available commands

- **Knowledge Base** (if configured):
  - `search colleges in California` - Search the knowledge base using RAG

### Diagnostic Tool

To check if the AI model is running correctly:

1. Click the "Run Diagnostic" button in the top-right corner
2. The diagnostic panel will show tests for model status, inference, commands, and TTS
3. If any test fails, expand the details to see specific error messages

## Troubleshooting

- **AI Model Connection Issues**: Make sure the API server is running and accessible
- **Command Execution Problems**: Check that you have the necessary permissions for system commands
- **Audio Issues**: Ensure your browser supports web audio and has permission to play sounds

## Requirements

- Node.js 16+
- Python 3.8+
- Internet connection for Gemini API access

## License

This project is licensed under the MIT License.
