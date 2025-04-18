"""
FastAPI server for AURA - Augmented User Response Assistant
This server handles requests from the Supabase Edge Functions and connects to Google's Gemini API.
"""
import os
import sys
import json
import time
import logging
import platform
import re
import subprocess
import webbrowser
from urllib.parse import urlparse
from typing import Dict, Any, Optional, List
from ctypes import cast, POINTER
from datetime import datetime

# Import dotenv for environment variables
try:
    from dotenv import load_dotenv
    dotenv_available = True
except ImportError:
    dotenv_available = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("api-server")

# FastAPI imports
from fastapi import FastAPI, Request, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Third-party imports
try:
    from slowapi import Limiter, _rate_limit_exceeded_handler
    from slowapi.util import get_remote_address
    from slowapi.errors import RateLimitExceeded
    rate_limiting_available = True
except ImportError:
    logger.warning("slowapi not installed, rate limiting will not be available")
    rate_limiting_available = False
    
try:
    from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
    huggingface_available = True
    logger.info("Hugging Face transformers imported successfully")
except ImportError:
    huggingface_available = False
    logger.warning("transformers not installed, Hugging Face model will not be available")
    
try:
    import google.generativeai as genai
    gemini_available = True
    logger.info("Gemini API imported successfully")
except ImportError:
    logger.warning("google.generativeai not installed, Gemini API will not be available")
    gemini_available = False

try:
    import pyngrok.conf
    from pyngrok import ngrok, conf
    ngrok_available = True
    logger.info("ngrok imported successfully")
except ImportError:
    logger.warning("pyngrok not installed, ngrok tunneling will not be available")
    ngrok_available = False
    
try:
    import uvicorn
    uvicorn_available = True
    logger.info("uvicorn imported successfully")
except ImportError:
    logger.warning("uvicorn not installed, server cannot be started")
    uvicorn_available = False

# Check Jarvis integration
try:
    import jarvis_bridge as aura_bridge
    aura_available = True
    logger.info("AURA core bridge imported successfully")
except ImportError:
    aura_available = False
    logger.warning("AURA core bridge not available")
    
# Check RAG integration
try:
    import rag_engine
    rag_available = True
    logger.info("RAG engine imported successfully")
except ImportError:
    rag_available = False
    logger.warning("RAG engine not available")

# Load environment variables
if dotenv_available:
    load_dotenv()
    logger.info("Loaded environment variables from .env file")
else:
    logger.warning("python-dotenv not installed, skipping .env file loading")

# Configure Gemini API
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyDT70dXIaCcjZsB8ktCGQlbMqLnQ5PW2RU")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-1.5-pro-latest") # Updated model name

# Configure Hugging Face model
HF_MODEL_NAME = os.environ.get("HF_MODEL_NAME", "naxwinn/qlora-jarvis-output")
# Don't use Hugging Face model on Vercel due to size limitations
USE_HUGGINGFACE = os.environ.get("USE_HUGGINGFACE", "true").lower() == "true" and os.environ.get("VERCEL_ENV") is None

# Import RAG assistant if available
try:
    from rag_assistant import query_rag_model
    rag_available = True
except ImportError:
    rag_available = False

# Global state
last_command_result = None
model_status = {
    "last_checked": 0,
    "online": False,
    "model": GEMINI_MODEL if not USE_HUGGINGFACE else HF_MODEL_NAME,
    "provider": "Google Gemini" if not USE_HUGGINGFACE else "Hugging Face",
    "memory_usage": None,
    "load": None
}

# Helper functions
def check_model_status() -> Dict[str, Any]:
    """Check if the AI model (Gemini API or Hugging Face) is available"""
    global model_status
    
    # Don't check more often than every 10 seconds
    current_time = time.time()
    if current_time - model_status["last_checked"] < 10:
        return model_status
    
    # Check Hugging Face model if enabled
    if huggingface_available and USE_HUGGINGFACE:
        try:
            if hf_model is None or hf_tokenizer is None:
                raise ValueError("Hugging Face model not properly initialized")
                
            # Simple test query to check if the model is responsive
            test_input = "Hello"
            test_prompt = f"User: {test_input}\n\nAssistant:"
            
            _ = hf_generator(
                test_prompt,
                max_length=50,
                num_return_sequences=1,
                pad_token_id=hf_tokenizer.eos_token_id,
                temperature=0.7
            )
            
            model_status.update({
                "last_checked": current_time,
                "online": True,
                "status": "Hugging Face model is online",
                "model": HF_MODEL_NAME,
                "provider": "Hugging Face",
                "memory_usage": "Local model",
                "load": 0.0  # We don't track load for local models
            })
            return model_status
        except Exception as e:
            logger.error(f"Error checking Hugging Face model status: {str(e)}")
            model_status.update({
                "last_checked": current_time,
                "online": False,
                "status": f"Error connecting to Hugging Face model: {str(e)}",
                "provider": "Hugging Face",
                "model": HF_MODEL_NAME
            })
            return model_status
    
    # Check Gemini API if Hugging Face is not enabled
    try:
        # Simple test query to check if the API is responsive
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content("Hello")
        
        model_status.update({
            "last_checked": current_time,
            "online": True,
            "status": "Gemini API is online",
            "model": GEMINI_MODEL,
            "provider": "Google Gemini",
            "memory_usage": "N/A (Cloud API)",
            "load": 0.0  # Cloud API doesn't expose load metrics
        })
        return model_status
        
    except Exception as e:
        logger.error(f"Error checking Gemini API status: {str(e)}")
        model_status.update({
            "last_checked": current_time,
            "online": False,
            "status": f"Error connecting to Gemini API: {str(e)}",
            "provider": "Google Gemini",
            "model": GEMINI_MODEL
        })
        return model_status

def query_huggingface(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Query the Hugging Face model"""
    try:
        if hf_generator is None:
            raise ValueError("Hugging Face model not loaded")
        
        # Format the prompt with system prompt if provided
        if system_prompt:
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            full_prompt = f"User: {prompt}\n\nAssistant:"
        
        # Generate response from the model
        response = hf_generator(
            full_prompt,
            max_length=1024,
            num_return_sequences=1,
            pad_token_id=hf_tokenizer.eos_token_id,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )
        
        # Extract the generated text and remove the prompt
        generated_text = response[0]['generated_text']
        answer = generated_text.split("Assistant:", 1)[-1].strip()
        
        return answer
    except Exception as e:
        logger.error(f"Error querying Hugging Face model: {str(e)}")
        return f"Error: {str(e)}"

def query_gemini(prompt: str, system_prompt: Optional[str] = None) -> str:
    """Query the Gemini API or Hugging Face model based on configuration"""
    # If Hugging Face model is available and enabled, use it instead of Gemini
    if huggingface_available and USE_HUGGINGFACE and hf_generator is not None:
        return query_huggingface(prompt, system_prompt)
        
    # Otherwise, use Gemini
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
        status = check_model_status()
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

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Initialize FastAPI app
app = FastAPI(
    title="AURA API",
    description="API server for AURA - Augmented User Response Assistant",
    version="1.0.0"
)

# Add rate limiter to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Mount static directory for serving audio files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Global error handler
@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """Global error handling middleware for all requests"""
    try:
        return await call_next(request)
    except Exception as e:
        logger.error(f"Unhandled exception in request: {str(e)}")
        
        # Get the exception traceback
        import traceback
        error_details = traceback.format_exc()
        logger.error(error_details)
        
        # Return a JSON response with error details
        return HTMLResponse(
            status_code=500,
            content={
                "success": False,
                "message": f"Internal server error: {str(e)}",
                "path": request.url.path,
                "timestamp": time.time(),
                "request_id": request.headers.get("X-Request-ID", "unknown")
            }
        )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize models
hf_model = None
hf_tokenizer = None
hf_generator = None

if huggingface_available and USE_HUGGINGFACE:
    try:
        logger.info(f"Loading Hugging Face model: {HF_MODEL_NAME}")
        hf_tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_NAME)
        hf_model = AutoModelForCausalLM.from_pretrained(HF_MODEL_NAME)
        hf_generator = pipeline("text-generation", model=hf_model, tokenizer=hf_tokenizer)
        logger.info("Hugging Face model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading Hugging Face model: {str(e)}")
        USE_HUGGINGFACE = False

# Configure Gemini if Hugging Face is not available or not used
if gemini_available and (not huggingface_available or not USE_HUGGINGFACE):
    genai.configure(api_key=GEMINI_API_KEY)
    logger.info(f"Using Gemini model: {GEMINI_MODEL}")
else:
    logger.info("Gemini API will not be used")

# Models
class MessageRequest(BaseModel):
    message: str

class CommandRequest(BaseModel):
    command: str
    use_jarvis: bool = False

class TTSRequest(BaseModel):
    text: str

# AURA-specific models
class AuraStatusResponse(BaseModel):
    initialized: bool
    running: bool
    components: Dict[str, bool]

class AuraActionRequest(BaseModel):
    action: str  # 'initialize', 'start', 'stop'

# Endpoints
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AURA API Server is running", "model": GEMINI_MODEL}

@app.get("/status")
async def status():
    """Get model status"""
    return check_model_status()

@app.post("/query")
@limiter.limit("20/minute")
async def query(request: MessageRequest, request_obj: Request):
    """Query the model with a message"""
    try:
        # Prepare system prompt
        system_prompt = "You are AURA, an advanced AI assistant. Provide helpful, accurate, and concise responses."
        
        # Get response from the model
        response = query_gemini(request.message, system_prompt)
        
        return {
            "success": True,
            "response": response,
            "model": GEMINI_MODEL
        }
    except Exception as e:
        logger.error(f"Error in query endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/execute")
@limiter.limit("10/minute")
async def execute(request: CommandRequest, background_tasks: BackgroundTasks, request_obj: Request):
    """Execute a command with AURA or AI models"""
    request_ip = request_obj.client.host
    logger.info(f"Execute command request from {request_ip}: {request.command}")
    
    if not request.command:
        return {"success": False, "message": "No command provided"}
    
    # Use AURA if requested
    if request.use_jarvis and aura_available:
        try:
            result = aura_bridge.process_aura_command(request.command)
            
            # Store the last command result
            global last_command_result
            last_command_result = {
                "command": request.command,
                "success": result.get("success", False),
                "message": result.get("message", ""),
                "data": result.get("data", {}),
                "timestamp": datetime.now().isoformat(),
                "using_aura": True
            }
            
            return result
        except Exception as e:
            logger.error(f"Error executing command with AURA: {str(e)}")
            return {"success": False, "message": f"Error: {str(e)}"}
    
    # Use AI models otherwise
    command_response = await execute_command(request.command)
    
    # Store the last command result
    global last_command_result
    last_command_result = {
        "command": request.command,
        "success": True,
        "message": command_response,
        "timestamp": datetime.now().isoformat(),
        "using_aura": False
    }
    
    return {"success": True, "message": command_response}

@app.post("/tts")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech"""
    try:
        from gtts import gTTS
        import uuid
        import os
        
        # Create a unique filename for this audio
        filename = f"tts_{uuid.uuid4()}.mp3"
        
        # Use public directory for Vercel, static directory otherwise
        if os.environ.get("VERCEL_ENV"):
            output_path = os.path.join("public", "static", "audio")
            audio_url_prefix = "/static/audio"  # Vercel serves files from public directly
        else:
            output_path = os.path.join("static", "audio")
            audio_url_prefix = "/static/audio"
        
        # Ensure directory exists
        os.makedirs(output_path, exist_ok=True)
        
        full_path = os.path.join(output_path, filename)
        
        # Generate speech using gTTS
        tts = gTTS(text=request.text, lang='en', slow=False)
        tts.save(full_path)
        
        # Return the URL to the audio file
        audio_url = f"{audio_url_prefix}/{filename}"
        
        # Calculate estimated duration (rough estimate: 150 chars per 10 seconds)
        duration = len(request.text) / 15
        
        return {
            "audioUrl": audio_url,
            "duration": duration
        }
    except ImportError:
        # Fallback to mock if gtts is not installed
        logger.warning("gtts not installed, using mock TTS response")
        return {
            "audioUrl": "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm.ogg",
            "duration": len(request.text) / 20
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

# Get AURA status
@app.get("/aura/status", response_model=AuraStatusResponse)
async def aura_status():
    """Get AURA system status"""
    if not aura_available:
        return {"initialized": False, "running": False, "components": {}}
    
    try:
        return aura_bridge.get_aura_status()
    except Exception as e:
        logger.error(f"Error getting AURA status: {str(e)}")
        return {"initialized": False, "running": False, "components": {}}

# Perform AURA action (initialize, start, stop)
@app.post("/aura/action")
async def aura_action(request: AuraActionRequest):
    """Perform an action on the AURA system (initialize, start, stop)"""
    if not aura_available:
        return {"success": False, "message": "AURA core integration is not available"}
    
    try:
        action = request.action.lower()
        
        if action == "initialize":
            result = aura_bridge.initialize_aura()
            return {"success": result, "message": "AURA initialized successfully" if result else "Failed to initialize AURA"}
        elif action == "start":
            result = aura_bridge.start_aura()
            return {"success": result, "message": "AURA started successfully" if result else "Failed to start AURA"}
        elif action == "stop":
            result = aura_bridge.stop_aura()
            return {"success": result, "message": "AURA stopped successfully" if result else "Failed to stop AURA"}
        else:
            return {"success": False, "message": f"Unknown action: {action}"}
    except Exception as e:
        logger.error(f"Error performing AURA action: {str(e)}")
        return {"success": False, "message": f"Error: {str(e)}"}

# Get available integrations
@app.get("/integrations")
async def get_integrations():
    """Get information about available integrations"""
    return {
        "huggingface": huggingface_available,
        "google_generative_ai": gemini_available,
        "rag": rag_available,
        "aura": aura_available,
        "api_status": model_status,
        "versions": {
            "api_server": "2.1.0",
            "rag_engine": "1.0.5" if rag_available else None,
            "aura_core": "2.0.0" if aura_available else None,
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
    }

if __name__ == "__main__":
    # This block only runs when executed directly, not on Vercel
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting AURA API server on port {port}")
    
    if USE_HUGGINGFACE and huggingface_available:
        logger.info(f"Using Hugging Face model: {HF_MODEL_NAME}")
    else:
        logger.info(f"Using Gemini API with key: {GEMINI_API_KEY[:5]}...")
    
    # Set up ngrok tunnel - only when running locally
    if ngrok_available and os.environ.get("VERCEL_ENV") is None:
        try:
            # Set up auth token if provided
            ngrok_auth_token = os.environ.get("NGROK_AUTH_TOKEN", "2vuDgkjBttqOoLWBXiPKZg2VfBd_3iNs6ZiMPfL9pHgNmGKFo")
            conf.get_default().auth_token = ngrok_auth_token
            
            # Configure ngrok with heartbeat monitoring
            conf.get_default().monitor_thread = True
            conf.get_default().heartbeat_interval = 30
            conf.get_default().reconnect_attempts = 5
            conf.get_default().reconnect_wait = 2
            
            # Start ngrok tunnel
            # Use the simplest connect method
            public_url = ngrok.connect(port).public_url
            logger.info(f"AURA API Server accessible via ngrok tunnel: {public_url}")
            logger.info(f"Use these URLs in your Supabase environment variables:")
            logger.info(f"GEMINI_API_URL: {public_url}/chat")
            logger.info(f"COMMAND_API_URL: {public_url}/execute")
            logger.info(f"STATUS_API_URL: {public_url}/status")
            logger.info(f"TTS_API_URL: {public_url}/tts")
            
            # Run the URL updater script to automatically update Supabase
            try:
                logger.info("Launching URL updater script to update Supabase environment variables...")
                # Start in a new process so it doesn't block the server
                subprocess.Popen(["python", "update_urls.py"])
            except Exception as e:
                logger.error(f"Failed to launch URL updater script: {str(e)}")
                logger.info("You will need to update Supabase environment variables manually")
                
            # Set up a background task to monitor ngrok tunnel health
            def monitor_tunnel():
                try:
                    import threading
                    import time
                    
                    def check_tunnel():
                        while True:
                            try:
                                # Check if the tunnel is still alive
                                tunnels = ngrok.get_tunnels()
                                if not tunnels:
                                    logger.warning("No active ngrok tunnels found! Attempting to reconnect...")
                                    new_tunnel = ngrok.connect(port)
                                    logger.info(f"Reestablished ngrok tunnel: {new_tunnel.public_url}")
                                    # Update Supabase variables with new URL
                                    subprocess.Popen(["python", "update_urls.py"])
                                time.sleep(60)  # Check every minute
                            except Exception as e:
                                logger.error(f"Error in tunnel monitoring: {str(e)}")
                                time.sleep(10)  # Wait before retrying
                    
                    # Start the monitoring in a background thread
                    monitor_thread = threading.Thread(target=check_tunnel, daemon=True)
                    monitor_thread.start()
                    logger.info("Started ngrok tunnel monitoring")
                    
                except Exception as e:
                    logger.error(f"Failed to set up tunnel monitoring: {str(e)}")
            
            # Start the monitoring
            monitor_tunnel()
                
        except Exception as e:
            logger.error(f"Failed to create ngrok tunnel: {str(e)}")
            logger.info("Continuing without ngrok tunnel...")
    
    uvicorn.run("api_server:app", host="0.0.0.0", port=port, reload=True)
else:
    # When imported by Vercel, log the initialization
    logger.info("AURA API initialized for serverless deployment")
    if USE_HUGGINGFACE and huggingface_available:
        logger.info(f"Using Hugging Face model: {HF_MODEL_NAME}")
    else:
        logger.info(f"Using Gemini API with key: {GEMINI_API_KEY[:5]}...") 