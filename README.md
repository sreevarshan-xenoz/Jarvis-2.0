# AURA API with Jarvis Model

This Hugging Face Space hosts the AURA (Augmented User Response Assistant) model, using the custom fine-tuned `naxwinn/qlora-jarvis-output` model.

## Features

### Chat Interface
- Conversational interface with the Jarvis model
- Support for system prompts to guide responses
- Chat history tracking

### Command Execution
- Execute commands through the model
- Built-in commands: `status`, `help`
- Model-interpreted commands for other inputs

### Status Monitoring
- Check model status
- Load/reload model when needed
- View model health information

## Integration with AURA Frontend

To connect your AURA frontend to this Gradio Space:

1. **Option 1**: Use the direct Gradio API endpoints:
   - The Gradio interface creates API endpoints at `/api/predict`
   - Check the API documentation by clicking the "API" tab in the Gradio interface

2. **Option 2**: Add a custom FastAPI backend to your project:
   - Use the model directly through Hugging Face's model repository
   - `from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline`
   - `model = AutoModelForCausalLM.from_pretrained("naxwinn/qlora-jarvis-output")`

## About the Model

This Space serves the `naxwinn/qlora-jarvis-output` model, which is a fine-tuned language model specifically for AURA assistant capabilities.

## Performance Notes

- The first request may take longer as the model needs to be loaded into memory
- Subsequent requests will be faster
- The model runs on CPU in the free tier, which might result in slower responses
