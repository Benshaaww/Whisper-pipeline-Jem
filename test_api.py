import requests
import os
import json

# This script verifies that the local FastAPI server can receive audio and return the pipeline result.
URL = "http://localhost:8000/process-audio/"

# 1. Create a dummy audio file
test_file_path = "whatsapp_test_audio.ogg"
with open(test_file_path, "wb") as f:
    f.write(b"simulated_audio_data_for_api_test")

print("Created dummy audio file.")

try:
    # 2. Open the file and send it as a multi-part form data POST request
    with open(test_file_path, "rb") as audio_file:
        files = {"audio_file": (test_file_path, audio_file, "audio/ogg")}
        print(f"Sending POST request to {URL}...")
        
        response = requests.post(URL, files=files)
        
    print(f"Status Code: {response.status_code}")
    
    try:
        # If it's a JSON response, print it nicely
        data = response.json()
        print(json.dumps(data, indent=4))
    except ValueError:
        # If it's not JSON, print the raw text
        print(response.text)
        
finally:
    # 3. Clean up the dummy file
    if os.path.exists(test_file_path):
        os.remove(test_file_path)
        print("Cleaned up dummy audio file.")
