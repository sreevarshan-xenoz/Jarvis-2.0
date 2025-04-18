import os
import logging
import time
import gradio as gr
from typing import Dict, Any, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("aura-api")

# Model configuration
MODEL_NAME = os.environ.get("MODEL_NAME", "naxwinn/qlora-jarvis-output")

# Global state for model
model = None
tokenizer = None
generator = None
model_loaded = False
model_status = {
    "last_checked": 0,
    "online": False,
    "model": MODEL_NAME,
    "provider": "Hugging Face",
    "memory_usage": None,
    "load": None
}

def load_model():
    """Load the model"""
    global model, tokenizer, generator, model_loaded, model_status
    
    try:
        logger.info(f"Loading model: {MODEL_NAME}")
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        generator = pipeline("text-generation", model=model, tokenizer=tokenizer)
        model_loaded = True
        model_status.update({
            "last_checked": time.time(),
            "online": True,
            "status": "Model loaded successfully",
            "model": MODEL_NAME,
        })
        logger.info("Model loaded successfully")
        return "Model loaded successfully"
    except Exception as e:
        model_loaded = False
        model_status.update({
            "last_checked": time.time(),
            "online": False,
            "status": f"Error loading model: {str(e)}",
            "model": MODEL_NAME,
        })
        error_msg = f"Error loading model: {str(e)}"
        logger.error(error_msg)
        return error_msg

def check_model_status():
    """Check if the model is available"""
    global model_status
    
    # Don't check more often than every 10 seconds
    current_time = time.time()
    if current_time - model_status["last_checked"] < 10:
        status_text = f"Model: {model_status['model']}\nStatus: {'Online' if model_status['online'] else 'Offline'}\nLast checked: {time.ctime(model_status['last_checked'])}"
        return status_text
    
    try:
        if not model_loaded or model is None or tokenizer is None:
            raise ValueError("Model not properly initialized")
            
        # Simple test query to check if the model is responsive
        test_input = "Hello"
        test_prompt = f"User: {test_input}\n\nAssistant:"
        
        _ = generator(
            test_prompt,
            max_length=50,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id,
            temperature=0.7
        )
        
        model_status.update({
            "last_checked": current_time,
            "online": True,
            "status": "Model is online",
            "model": MODEL_NAME,
            "provider": "Hugging Face",
        })
    except Exception as e:
        logger.error(f"Error checking model status: {str(e)}")
        model_status.update({
            "last_checked": current_time,
            "online": False,
            "status": f"Error: {str(e)}",
            "provider": "Hugging Face",
            "model": MODEL_NAME
        })
    
    status_text = f"Model: {model_status['model']}\nStatus: {'Online' if model_status['online'] else 'Offline'}\nLast checked: {time.ctime(model_status['last_checked'])}"
    if not model_status['online']:
        status_text += f"\nError: {model_status['status']}"
    
    return status_text

def query_model(prompt, system_prompt=None):
    """Query the model"""
    global model, tokenizer, generator, model_loaded
    
    try:
        if not model_loaded:
            load_model()
            if not model_loaded:
                return "Error: Model not available"
        
        # Format the prompt with system prompt if provided
        if system_prompt and system_prompt.strip():
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\n\nAssistant:"
        else:
            full_prompt = f"User: {prompt}\n\nAssistant:"
        
        # Generate response from the model
        response = generator(
            full_prompt,
            max_length=1024,
            num_return_sequences=1,
            pad_token_id=tokenizer.eos_token_id,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )
        
        # Extract the generated text and remove the prompt
        generated_text = response[0]['generated_text']
        answer = generated_text.split("Assistant:", 1)[-1].strip()
        
        return answer
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        logger.error(f"Error querying model: {str(e)}")
        return error_msg

def execute_command(command):
    """Handle command execution"""
    # For Spaces deployment, we'll use a simplified command handler
    # that doesn't actually execute system commands but responds appropriately
    
    # Status command
    if command in ["status", "health", "check"]:
        return check_model_status()
    
    # Help command
    elif command in ["help", "commands", "?"]:
        return "Available commands: status, help"
    
    # For other commands, pass to the model
    else:
        return query_model(f"Execute command: {command}")

# Set up the Gradio interface
def setup_gradio():
    with gr.Blocks(title="AURA API", css="footer {visibility: hidden}") as demo:
        gr.Markdown("# AURA API - Jarvis Model Interface")
        
        with gr.Tab("Chat"):
            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(label="Chat History")
                    msg = gr.Textbox(placeholder="Type a message...", label="Message")
                    
                    with gr.Row():
                        submit_btn = gr.Button("Send", variant="primary")
                        clear_btn = gr.Button("Clear")
                
                with gr.Column(scale=1):
                    system_prompt = gr.Textbox(
                        placeholder="Optional system prompt...",
                        label="System Prompt",
                        lines=5
                    )
            
            def user_message(user_message, history, system_prompt):
                # Add user message to history
                history.append((user_message, None))
                return "", history
            
            def bot_message(history, system_prompt):
                # Get last user message
                user_message = history[-1][0]
                
                # Query model for response
                bot_response = query_model(user_message, system_prompt)
                
                # Update history with bot response
                history[-1] = (user_message, bot_response)
                return history
            
            submit_btn.click(
                user_message, 
                [msg, chatbot, system_prompt], 
                [msg, chatbot]
            ).then(
                bot_message,
                [chatbot, system_prompt],
                [chatbot]
            )
            
            clear_btn.click(lambda: [], [], [chatbot])
        
        with gr.Tab("Commands"):
            command_input = gr.Textbox(placeholder="Enter command (e.g., 'status', 'help')", label="Command")
            command_output = gr.Textbox(label="Output", lines=10)
            
            command_btn = gr.Button("Execute")
            
            command_btn.click(
                execute_command,
                [command_input],
                [command_output]
            )
        
        with gr.Tab("Status"):
            status_output = gr.Textbox(label="Model Status", lines=10)
            status_btn = gr.Button("Check Status")
            load_model_btn = gr.Button("Load/Reload Model")
            
            status_btn.click(
                check_model_status,
                [],
                [status_output]
            )
            
            load_model_btn.click(
                load_model,
                [],
                [status_output]
            )
        
        # Load model on startup
        demo.load(
            check_model_status,
            [],
            [status_output]
        )
        
    return demo

# Create and launch the Gradio interface
demo = setup_gradio()

if __name__ == "__main__":
    # When running locally
    demo.launch()
else:
    # For Hugging Face Spaces
    demo.launch(share=False) 