# AURA Setup Guide

This guide will walk you through setting up the AURA (Augmented User Response Assistant) application.

## Prerequisites

- Node.js 16+ for the frontend
- Python 3.8+ for the API server
- Docker & Docker Compose (optional, for containerized deployment)
- ngrok authtoken (for exposing local services)
- Gemini API key from Google AI Studio

## Quick Start

### Option 1: Manual Setup

1. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your:
   - `GEMINI_API_KEY`
   - `NGROK_AUTH_TOKEN`

2. **Install API server dependencies**:
   ```bash
   pip install -r api_requirements.txt
   ```

3. **Start the API server**:
   ```bash
   python api_server.py
   ```
   The server will start on port 8000 and create an ngrok tunnel.

4. **Install frontend dependencies**:
   ```bash
   npm install
   ```

5. **Start the frontend**:
   ```bash
   npm start
   ```
   The frontend will be available at http://localhost:3000.

### Option 2: Docker Setup

1. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your API keys.

2. **Start with Docker Compose**:
   ```bash
   docker-compose up -d
   ```
   This will start both the API server and frontend.

3. **Access the application** at http://localhost:3000.

## Supabase Edge Functions Setup

To deploy the Edge Functions to Supabase:

1. **Install the Supabase CLI**:
   ```bash
   # Option 1: Using scoop (Windows)
   scoop bucket add extras
   scoop install supabase

   # Option 2: Using Homebrew
   brew install supabase/tap/supabase
   ```

2. **Deploy the functions**:
   ```bash
   npx supabase@latest functions deploy
   ```

3. **Set environment variables** (automatically done by the `update_urls.py` script):
   ```bash
   npx supabase@latest secrets set GEMINI_API_URL="https://your-ngrok-url/chat" COMMAND_API_URL="https://your-ngrok-url/execute" STATUS_API_URL="https://your-ngrok-url/status" TTS_API_URL="https://your-ngrok-url/tts"
   ```

## Features

AURA includes several key features:

- **AI Chat**: Communicate with the Gemini AI model
- **Command Execution**: Run system commands through the interface
- **Voice Interaction**: Text-to-speech capabilities
- **Diagnostic Tools**: Verify AI and service connectivity
- **Themes**: Switch between light and dark themes
- **Persistence**: Chat history saved locally

## Troubleshooting

### Ngrok Issues
- If ngrok isn't connecting, check your internet connection
- Verify your authtoken in the `.env` file
- Run `ngrok authtoken YOUR_TOKEN` manually

### API Connection Issues
- Check the "Run Diagnostic" panel for specific failures
- Ensure your Gemini API key is valid
- Verify that all environment variables are set correctly

### Docker Issues
- Make sure Docker and Docker Compose are installed
- Check container logs with `docker-compose logs`

## Security Considerations

- AURA includes rate limiting to prevent API abuse
- API keys are stored locally in the `.env` file
- Docker containerization isolates the application

## Advanced Configuration

For advanced configuration options:

- Edit `api_server.py` to modify server behavior
- Adjust ngrok settings in the code for custom domains
- Modify `.env` variables for different API keys or models

## Updates and Maintenance

To update AURA:

1. Pull the latest changes:
   ```bash
   git pull origin main
   ```

2. Update dependencies:
   ```bash
   pip install -r api_requirements.txt
   npm install
   ```

3. Restart the services:
   ```bash
   # For manual setup
   python api_server.py
   npm start

   # For Docker setup
   docker-compose up -d --build
   ``` 