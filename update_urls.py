import os
import json
import time
import requests
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("url-updater")

def update_supabase_urls():
    """Get current ngrok URL and update Supabase environment variables"""
    try:
        # Wait a moment for ngrok API to be available
        time.sleep(3)
        
        # Get current ngrok URL from the local API
        response = requests.get("http://localhost:4040/api/tunnels")
        data = response.json()
        
        # Extract the https tunnel URL
        tunnels = data["tunnels"]
        ngrok_url = None
        
        for tunnel in tunnels:
            if tunnel["proto"] == "https":
                ngrok_url = tunnel["public_url"]
                break
        
        if not ngrok_url:
            logger.error("No HTTPS tunnel found in ngrok")
            return False
        
        logger.info(f"Found ngrok URL: {ngrok_url}")
        
        # Update Supabase environment variables
        cmd = f'''npx supabase@latest secrets set GEMINI_API_URL="{ngrok_url}/chat" COMMAND_API_URL="{ngrok_url}/execute" STATUS_API_URL="{ngrok_url}/status" TTS_API_URL="{ngrok_url}/tts"'''
        
        logger.info("Updating Supabase environment variables...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("Successfully updated Supabase environment variables")
            logger.info("URLs set to:")
            logger.info(f"GEMINI_API_URL: {ngrok_url}/chat")
            logger.info(f"COMMAND_API_URL: {ngrok_url}/execute")
            logger.info(f"STATUS_API_URL: {ngrok_url}/status")
            logger.info(f"TTS_API_URL: {ngrok_url}/tts")
            return True
        else:
            logger.error(f"Failed to update Supabase environment variables: {result.stderr}")
            return False
            
    except requests.RequestException as e:
        logger.error(f"Error connecting to ngrok API: {str(e)}")
        logger.info("Make sure ngrok is running and the API is available at http://localhost:4040")
        return False
    except Exception as e:
        logger.error(f"Unexpected error updating URLs: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting URL updater script")
    update_supabase_urls() 