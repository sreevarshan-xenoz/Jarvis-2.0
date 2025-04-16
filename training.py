import requests
import os
import shutil
import time
import subprocess
import json

def fine_tune_model():
    """Fine-tune using Ollama CLI for reliability"""
    dataset_path = "./college_admissions_dataset.jsonl"
    if not os.path.exists(dataset_path):
        print(f"Error: Missing dataset at {os.path.abspath(dataset_path)}")
        return False
        
    # Validate dataset format
    try:
        with open(dataset_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            if not lines:
                print("Error: Dataset is empty")
                return False
            for i, line in enumerate(lines, 1):
                try:
                    data = json.loads(line.strip())
                    if not all(k in data for k in ['prompt', 'response']):
                        print(f"Error: Line {i} missing required fields")
                        return False
                except json.JSONDecodeError:
                    print(f"Error: Invalid JSON at line {i}")
                    return False
    except Exception as e:
        print(f"Error reading dataset: {str(e)}")
        return False

    # Prepare training directory
    ollama_data_dir = os.path.abspath("./ollama_data")
    os.makedirs(ollama_data_dir, exist_ok=True)
    
    # Copy dataset
    dataset_basename = os.path.basename(dataset_path)
    shutil.copy2(dataset_path, os.path.join(ollama_data_dir, dataset_basename))
    
    # Create Modelfile (Critical fix: proper formatting)
    modelfile_content = f"""FROM gemma:2b

SYSTEM \"\"\"You are an expert college admissions assistant for SRM University.Answer questions about admissions, programs, housing, and fees using official information.Be professional but friendly.\"\"\"

TRAIN {dataset_basename}
PARAMETER temperature 0.3
"""
    modelfile_path = os.path.join(ollama_data_dir, "Modelfile")
    with open(modelfile_path, "w") as f:
        f.write(modelfile_content)

    # Train using CLI (More reliable than API)
    try:
        result = subprocess.run(
            ["ollama", "create", "college-assistant", "-f", modelfile_path],
            capture_output=True,
            text=True,
            timeout=1200  # 20-minute timeout
        )
        
        if result.returncode == 0:
            print("Model created successfully. Allow 2 minutes for initialization.")
            return True
            
        print(f"Training failed. Ollama output:\n{result.stderr}")
        return False
        
    except Exception as e:
        print(f"Training error: {str(e)}")
        return False

def validate_training():
    print("Starting validation in 60 seconds...")
    time.sleep(60)  # Critical: Increased wait time
    
    # Test multiple aspects of the model
    test_cases = [
        {
            "question": "What's the application deadline?",
            "keywords": ["january", "15", "regular", "admission"]
        },
        {
            "question": "What are the required documents?",
            "keywords": ["application", "form", "mark", "sheets", "certificate"]
        }
    ]
    
    failures = 0
    
    try:
        for test_case in test_cases:
            print(f"\nTesting: {test_case['question']}")
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "college-assistant",
                    "prompt": test_case['question'],
                    "stream": False
                },
                timeout=30
            )
            
            if not response.ok:
                print(f"Validation HTTP Error: {response.status_code}")
                failures += 1
                continue

            answer = response.json().get("response", "").lower()
            print(f"Model Response: {answer}")
            
            missing_keywords = [k for k in test_case['keywords'] if k not in answer]
            if missing_keywords:
                print(f"❌ Failed - Missing keywords: {', '.join(missing_keywords)}")
                failures += 1
            else:
                print("✅ Passed!")
                
        if failures == 0:
            print("\n✅ All validation tests passed!")
        else:
            print(f"\n❌ {failures} test(s) failed - Model may need retraining")
            
    except Exception as e:
        print(f"Validation Error: {str(e)}")

def main():
    print("=== College Admissions Assistant Training ===")
    
    # Verify Ollama running
    try:
        subprocess.run(["ollama", "serve"], check=True, startupinfo=subprocess.STARTUPINFO())
    except:
        print("Error: Start Ollama first with 'ollama serve'")
        return
    
    if fine_tune_model():
        validate_training()

if __name__ == "__main__":
    main()