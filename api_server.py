"""
FastAPI server for AURA - Augmented User Response Assistant
This server handles requests from the Supabase Edge Functions and connects to Google's Gemini API.
"""
import os
import json
import time
import logging
import requests
import subprocess
import webbrowser
import platform
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import google.generativeai as genai
from dotenv import load_dotenv
from urllib.parse import urlparse
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
# Comment out problematic import and add alternative implementation
# from comtypes.win32 import AudioUtilities, IAudioEndpointVolume
import re

# Load environment variables
load_dotenv()

# Import RAG assistant if available
try:
    from rag_assistant import query_rag_model
    rag_available = True
except ImportError:
    rag_available = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aura-api")

# Initialize FastAPI app
app = FastAPI(
    title="AURA API",
    description="API server for AURA - Augmented User Response Assistant",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDT70dXIaCcjZsB8ktCGQlbMqLnQ5PW2RU")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro-latest") # Updated model name
genai.configure(api_key=GEMINI_API_KEY)

# Models
class MessageRequest(BaseModel):
    message: str

class CommandRequest(BaseModel):
    command: str

class TTSRequest(BaseModel):
    text: str

# Global state
last_command_result = None
model_status = {
    "last_checked": 0,
    "online": False,
    "model": GEMINI_MODEL,
    "memory_usage": None,
    "load": None
}

# Helper functions
def check_gemini_status() -> Dict[str, Any]:
    """Check if Gemini API is available"""
    global model_status
    
    # Don't check more often than every 10 seconds
    current_time = time.time()
    if current_time - model_status["last_checked"] < 10:
        return model_status
    
    try:
        # Simple test query to check if the API is responsive
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content("Hello")
        
        model_status.update({
            "last_checked": current_time,
            "online": True,
            "status": "Gemini API is online",
            "model": GEMINI_MODEL,
            "memory_usage": "N/A (Cloud API)",
            "load": 0.0  # Cloud API doesn't expose load metrics
        })
        return model_status
        
    except Exception as e:
        logger.error(f"Error checking Gemini API status: {str(e)}")
        model_status.update({
            "last_checked": current_time,
            "online": False,
            "status": f"Error connecting to Gemini API: {str(e)}"
        })
        return model_status

def query_gemini(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Query the Gemini API"""
    try:
        # Configure the model
        generation_config = {
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 1024,
        }
        
        safety_settings = [
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        ]
        
        model = genai.GenerativeModel(
            model_name=GEMINI_MODEL,
            generation_config=generation_config,
            safety_settings=safety_settings
        )
        
        # Create a chat session
        chat = model.start_chat(history=[])
        
        # Add system prompt if provided
        if system_prompt:
            chat.send_message(system_prompt)
        
        # Send the user prompt and get response
        response = chat.send_message(prompt)
        return response.text
        
    except Exception as e:
        logger.error(f"Error querying Gemini API: {str(e)}")
        return f"Error: {str(e)}"

def open_website(url: str) -> str:
    """Open a website in the default browser"""
    try:
        # Ensure the URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            
        # Validate URL format
        parsed_url = urlparse(url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            return f"Invalid URL format: {url}"
        
        # Open the URL in the default browser
        webbrowser.open(url)
        return f"Opened website: {url}"
    except Exception as e:
        logger.error(f"Error opening website: {str(e)}")
        return f"Error opening website: {str(e)}"

# Define volume control alternatives based on platform
def get_volume_control():
    """Create platform-specific volume control functionality"""
    system = platform.system()
    
    if system == "Windows":
        try:
            # Try to import Windows-specific modules
            from comtypes import CLSCTX_ALL
            import pythoncom
            import pycaw.pycaw as pycaw
            
            def control_volume_windows(command):
                pythoncom.CoInitialize()
                devices = pycaw.AudioUtilities.GetSpeakers()
                interface = devices.Activate(pycaw.IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
                volume = cast(interface, POINTER(pycaw.IAudioEndpointVolume))
                
                if "mute" in command.lower():
                    volume.SetMute(1, None)
                    return "System volume muted"
                elif "unmute" in command.lower():
                    volume.SetMute(0, None)
                    return "System volume unmuted"
                elif "up" in command.lower() or "increase" in command.lower():
                    current_volume = volume.GetMasterVolumeLevelScalar()
                    new_volume = min(1.0, current_volume + 0.1)
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    return f"Volume increased to {int(new_volume * 100)}%"
                elif "down" in command.lower() or "decrease" in command.lower():
                    current_volume = volume.GetMasterVolumeLevelScalar()
                    new_volume = max(0.0, current_volume - 0.1)
                    volume.SetMasterVolumeLevelScalar(new_volume, None)
                    return f"Volume decreased to {int(new_volume * 100)}%"
                elif "set" in command.lower():
                    match = re.search(r'(\d+)', command)
                    if match:
                        percent = min(100, max(0, int(match.group(1))))
                        volume.SetMasterVolumeLevelScalar(percent / 100.0, None)
                        return f"Volume set to {percent}%"
                    else:
                        return "Could not extract volume percentage from command"
                else:
                    return "Unknown volume command. Use 'mute', 'unmute', 'up', 'down', or 'set X%'"
            
            return control_volume_windows
            
        except ImportError:
            logger.warning("Windows volume control libraries not available, using mock implementation")
    
    # For non-Windows systems or if Windows libraries failed to import
    def control_volume_mock(command):
        if "mute" in command.lower():
            return "System volume muted (mock)"
        elif "unmute" in command.lower():
            return "System volume unmuted (mock)"
        elif "up" in command.lower() or "increase" in command.lower():
            return "Volume increased (mock)"
        elif "down" in command.lower() or "decrease" in command.lower():
            return "Volume decreased (mock)"
        elif "set" in command.lower():
            match = re.search(r'(\d+)', command)
            if match:
                percent = min(100, max(0, int(match.group(1))))
                return f"Volume set to {percent}% (mock)"
            else:
                return "Could not extract volume percentage from command"
        else:
            return "Unknown volume command. Use 'mute', 'unmute', 'up', 'down', or 'set X%'"
    
    return control_volume_mock

# Set the volume control function based on platform
control_volume = get_volume_control()

def execute_command(command: str) -> Dict[str, Any]:
    """Execute a command and return the result"""
    global last_command_result
    
    # Normalize the command
    command = command.lower().strip()
    
    # Website opening commands
    if command.startswith(("open ", "go to ", "navigate to ", "browse ")):
        parts = command.split(" ", 1)
        if len(parts) > 1:
            website = parts[1].strip()
            # Remove common prefixes if present
            for prefix in ["http://", "https://", "www."]:
                if website.startswith(prefix):
                    website = website[len(prefix):]
            
            # Handle special website names
            if website in ["google", "google.com"]:
                return open_website("google.com")
            elif website in ["youtube", "youtube.com"]:
                return open_website("youtube.com")
            elif website in ["github", "github.com"]:
                return open_website("github.com")
            else:
                return open_website(website)
    
    # Volume control commands
    if "volume" in command or "sound" in command:
        return control_volume(command)
    
    # Check for RAG commands
    if rag_available and ("search" in command or "find" in command or "lookup" in command):
        try:
            # Extract the query from the command
            query = command.split(" ", 1)[1] if " " in command else command
            result = query_rag_model(query)
            if "error" in result:
                return {
                    "success": False,
                    "message": f"RAG query failed: {result['error']}",
                    "command": command
                }
            return {
                "success": True,
                "message": "Found information in knowledge base",
                "result": result["answer"],
                "command": command
            }
        except Exception as e:
            logger.error(f"Error executing RAG query: {str(e)}")
            return {
                "success": False,
                "message": f"Error executing RAG query: {str(e)}",
                "command": command
            }
    
    # Status command
    if command in ["status", "health", "check"]:
        status = check_gemini_status()
        return {
            "success": True,
            "message": f"System status: {status['status']}",
            "result": status,
            "command": command
        }
    
    # Help command
    if command in ["help", "commands", "usage"]:
        return {
            "success": True,
            "message": "Available commands",
            "result": [
                "open [website] - Open a website in the default browser",
                "volume up/down/mute/unmute - Control system volume",
                "volume set [level] - Set system volume to a specific level",
                "status - Check system status",
                "search [query] - Search knowledge base",
                "help - Show available commands"
            ],
            "command": command
        }
    
    # Unknown command - ask the model
    try:
        response = query_gemini(
            f"The user has issued the command: '{command}'. Please explain what this command might do, or if it's not a valid command, suggest alternatives.",
            system_prompt="You are AURA, an Augmented User Response Assistant. Respond to user commands helpfully and concisely."
        )
        
        return {
            "success": True,
            "message": "Command processed",
            "result": response,
            "command": command
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error processing command: {str(e)}",
            "command": command
        }

# Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AURA API Server is running", "model": GEMINI_MODEL}

@app.get("/status")
async def status():
    """Get model status"""
    return check_gemini_status()

@app.post("/query")
async def query(request: MessageRequest):
    """Query the Gemini model"""
    logger.info(f"Query received: {request.message}")
    
    # Check if RAG should be used
    if rag_available and "use rag" in request.message.lower():
        try:
            response = query_rag_model(request.message)
            return {
                "response": response,
                "model": "RAG-Assistant"
            }
        except Exception as e:
            logger.error(f"Error querying RAG model: {str(e)}")
    
    # Default to Gemini
    try:
        system_prompt = """You are AURA, a helpful AI assistant. Always be concise, helpful, and direct in your responses.
        Focus on providing accurate and relevant information. If you don't know something, admit it."""
        
        response = query_gemini(request.message, system_prompt)
        return {
            "response": response,
            "model": GEMINI_MODEL
        }
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        return {"response": f"Error: {str(e)}", "model": "Error"}

@app.post("/execute")
async def execute(request: CommandRequest, background_tasks: BackgroundTasks):
    """Execute a command"""
    global last_command_result
    
    try:
        result = execute_command(request.command)
        last_command_result = result
        return result
    except Exception as e:
        logger.error(f"Error executing command: {str(e)}")
        return {
            "success": False,
            "message": f"Error executing command: {str(e)}",
            "command": request.command
        }

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    # This is a mock implementation
    # In a real implementation, you would integrate with a TTS service
    
    try:
        # Mock TTS response
        return {
            "audioUrl": "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm.ogg",
            "duration": len(request.text) / 20  # Rough estimate: 20 chars per second
        }
    except Exception as e:
        logger.error(f"Error in TTS endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/last-command")
async def get_last_command():
    """Get the result of the last executed command"""
    if last_command_result is None:
        return {"message": "No command has been executed yet"}
    return last_command_result

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting AURA API server on port {port}")
    logger.info(f"Using Gemini API with key: {GEMINI_API_KEY[:5]}...")
    
    # Set up ngrok tunnel
    try:
        from pyngrok import ngrok, conf
        # Set up auth token if provided
        ngrok_auth_token = os.environ.get("NGROK_AUTH_TOKEN", "2vuDgkjBttqOoLWBXiPKZg2VfBd_3iNs6ZiMPfL9pHgNmGKFo")
        conf.get_default().auth_token = ngrok_auth_token
        
        # Start ngrok tunnel
        # Use the simplest connect method
        public_url = ngrok.connect(port).public_url
        logger.info(f"AURA API Server accessible via ngrok tunnel: {public_url}")
        logger.info(f"Use these URLs in your Supabase environment variables:")
        logger.info(f"GEMINI_API_URL: {public_url}/chat")
        logger.info(f"COMMAND_API_URL: {public_url}/execute")
        logger.info(f"STATUS_API_URL: {public_url}/status")
        logger.info(f"TTS_API_URL: {public_url}/tts")
    except Exception as e:
        logger.error(f"Failed to create ngrok tunnel: {str(e)}")
        logger.info("Continuing without ngrok tunnel...")
    
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True) 