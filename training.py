import requests
import json
import time
import os

def fine_tune_model():
    """Fine-tune the Gemma model using the college admissions dataset"""
    
    # Ollama API endpoint for creating/training models
    api_url = "http://localhost:11434/api/create"
    
    # Check if the dataset exists
    dataset_path = "./college_admissions_dataset.jsonl"
    if not os.path.exists(dataset_path):
        dataset_path = "./jarvis/college_admissions_dataset.jsonl"
        if not os.path.exists(dataset_path):
            print(f"Error: Could not find the dataset file at {dataset_path}")
            return False
    
    print(f"Using dataset: {dataset_path}")
    
    # Get the absolute path of the dataset file
    abs_dataset_path = os.path.abspath(dataset_path)
    print(f"Absolute dataset path: {abs_dataset_path}")
    
    # Create a directory for Ollama to access the dataset
    ollama_data_dir = "./ollama_data"
    os.makedirs(ollama_data_dir, exist_ok=True)
    
    # Copy the dataset to the Ollama data directory
    dataset_basename = os.path.basename(dataset_path)
    ollama_dataset_path = os.path.join(ollama_data_dir, dataset_basename)
    import shutil
    shutil.copy2(dataset_path, ollama_dataset_path)
    print(f"Copied dataset to: {ollama_dataset_path}")
    
    # Create a Modelfile that references the dataset
    modelfile_content = fFROM gemma:2b

SYSTEM """
You are an expert college admissions assistant for Springfield University. 
Answer questions about admissions, programs, housing, and fees using 
official information. Be professional but friendly.
"""

TRAIN ./college_admissions.jsonl

PARAMETER temperature 0.3
    
    # Write the Modelfile to the Ollama data directory
    modelfile_path = os.path.join(ollama_data_dir, "Modelfile")
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)
    print(f"Created Modelfile at: {modelfile_path}")
    
    # Prepare the request payload
    payload = {
        "name": "college-assistant",  # Name for the fine-tuned model
        "modelfile": modelfile_content,
        "stream": False,
        # The API requires either 'from' or 'files' parameter
        # We're using the modelfile which already has the FROM directive
        # Adding path to help Ollama locate the dataset file
        "path": ollama_data_dir  # Directory containing both Modelfile and dataset
    }
    
    # The error suggests we need to explicitly include the 'from' parameter
    # Adding it based on the Modelfile content
    payload["from"] = "gemma:2b"
    
    print("Payload prepared. Starting fine-tuning process...")
    print("This may take a while depending on your hardware and dataset size.")
    
    try:
        # Send the request to Ollama API
        response = requests.post(api_url, json=payload)
        
        # Check if the request was successful
        if response.status_code == 200:
            print("Fine-tuning completed successfully!")
            print("Your model 'college-assistant' is now available for use.")
            print("\nYou can use it with: ollama run college-assistant")
            return True
        else:
            print(f"Error: {response.status_code}")
            print(f"Error details: {response.text}")
            print("\nTroubleshooting tips:")
            print("1. Make sure Ollama can access the dataset file.")
            print("2. Try manually creating the model with: ollama create college-assistant -f ./ollama_data/Modelfile")
            print("3. Check Ollama logs for more details.")
            return False
            
    except Exception as e:
        print(f"An error occurred during fine-tuning: {e}")
        print("\nTroubleshooting tips:")
        print("1. Make sure Ollama is running.")
        print("2. Check your network connection.")
        print("3. Try manually creating the model with: ollama create college-assistant -f ./ollama_data/Modelfile")
        return False

def validate_training():
    test_question = "What's the application deadline?"  # From your dataset
    expected_answer = "January 15th"  # From your dataset
    
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "college-assistant",
            "prompt": test_question,
            "stream": False
        }
    )
    
    if expected_answer in response.json()['response']:
        print("✅ Validation passed!")
    else:
        print("❌ Training failed - response doesn't match dataset")

def main():
    print("=== Gemma Model Fine-tuning for College Admissions Assistant ===")
    print("Make sure Ollama is running before proceeding.")
    
    # Check if Ollama is running
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code != 200:
            print("Error: Could not connect to Ollama. Make sure it's running.")
            return
    except:
        print("Error: Could not connect to Ollama. Make sure it's running.")
        return
    
    print("Ollama is running. Proceeding with fine-tuning...\n")
    
    # Start the fine-tuning process
    success = fine_tune_model()
    
    if success:
        print("\nFine-tuning completed! Running validation...")
        validate_training()
    else:
        print("\nFine-tuning process failed. Please check the errors above.")

if __name__ == "__main__":
    main()