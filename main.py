# Server requirement: install the openai package
# pip install openai

import os
import json
import logging
from pathlib import Path
from typing import Optional
from openai import OpenAI, APIError, APIConnectionError, RateLimitError

# Set up logging so we can track the health and status of the pipeline
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

def validate_whatsapp_voice_note(file_path: str) -> bool:
    """
    Checks if the audio file exists and is in a valid format before we try to process it.
    
    This helps us save API costs and prevents errors if a user uploaded a broken 
    or empty file due to a bad network connection.
    
    Args:
        file_path (str): The local path to the downloaded WhatsApp voice note.
        
    Returns:
        bool: True if the file looks good to process, False otherwise.
    """
    valid_extensions = {".ogg", ".mp3", ".m4a", ".wav", ".webm", ".mp4"}
    path = Path(file_path)
    
    if not path.exists():
        logger.error(f"Validation Error: The audio file '{file_path}' does not exist.")
        return False
        
    if path.suffix.lower() not in valid_extensions:
        logger.error(f"Validation Error: Unsupported audio format '{path.suffix}'.")
        return False
        
    if path.stat().st_size == 0:
        logger.error("Validation Error: The audio file is empty (0 bytes).")
        return False
        
    return True

def translate_worker_voice_note_to_english(client: OpenAI, file_path: str) -> Optional[str]:
    """
    Transcribes the audio and translates it into an English text string.
    
    This is the core feature that solves the language barrier. It allows workers to speak 
    in their native language, and the AI converts it to English text so the rest of the 
    HR platform can understand the request.
    
    Args:
        client (OpenAI): The OpenAI API connection.
        file_path (str): The path to the audio file.
        
    Returns:
        Optional[str]: The translated English text, or nothing if there was an error.
    """
    logger.info(f"Initiating AI translation for worker voice note: {file_path}")
    
    try:
        with open(file_path, "rb") as audio_file:
            # Send the audio file to OpenAI to turn the voice into English text
            response = client.audio.translations.create(
                model="whisper-1",
                file=audio_file,
                response_format="text"
            )
            
            # Clean up the returned text
            extracted_text = str(response).strip()
            logger.info("Successfully converted the voice note to English.")
            return extracted_text
            
    # Handle possible errors (e.g., bad internet connection to OpenAI or account limits)
    except APIConnectionError as e:
        logger.error(f"Network Error: Failed to connect to OpenAI API. Details: {e}")
    except RateLimitError as e:
        logger.error(f"Rate Limit Error: OpenAI quota exceeded. Details: {e}")
    except APIError as e:
        logger.error(f"API Error during translation. Details: {e}")
    except Exception as e:
        logger.error(f"Unexpected Error during audio processing: {e}")
        
    return None

def dispatch_english_intent_to_hr_agent(translated_text: str) -> dict:
    """
    Sends the English text to the HR system to handle the worker's request.
    
    Once we have the clean English text, this step routes it to the correct 
    HR tool (like checking leave balances or logging a grievance).
    
    Args:
        translated_text (str): The English text intent.
        
    Returns:
        dict: A summary of the action the HR system took.
    """
    logger.info(f"Dispatching intent to ReAct HR Agent: '{translated_text}'")
    
    # In a real system, this connects to the actual HR backend. 
    # For now, we simulate a successful HR response.
    simulated_agent_state = {
        "status": "success",
        "identified_domain": "hr_leave_management",
        "action_taken": "query_leave_balance_tool",
        "original_input": translated_text,
        "agent_response": "I have checked your profile. You have 14 days of annual leave remaining."
    }
    
    logger.info("HR agent successfully processed the worker intent.")
    return simulated_agent_state

def process_whatsapp_audio_to_intent(file_path: str, openai_api_key: Optional[str] = None) -> Optional[dict]:
    """
    The main flow: Checks the file -> Translates it to English -> Sends it to HR.
    
    This function runs the complete process securely and catches any errors.
    
    Args:
        file_path (str): The path to the WhatsApp voice note.
        openai_api_key (Optional[str]): OpenAI API key.
        
    Returns:
        Optional[dict]: The final response from the HR system, or nothing if an error occurred.
    """
    logger.info("--- Starting WhatsApp Audio-to-Intent Pipeline ---")
    
    # 1. Check if the audio file is valid
    if not validate_whatsapp_voice_note(file_path):
        logger.error("Process stopped: Invalid audio file.")
        return None
        
    # Set up the connection to OpenAI
    try:
        client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        logger.error(f"Failed to set up OpenAI client. Details: {e}")
        return None

    # 2. Translate the audio to English text
    english_intent = translate_worker_voice_note_to_english(client, file_path)
    if not english_intent:
        logger.error("Process stopped: Could not translate the audio.")
        return None
        
    logger.info(f"Pipeline State -> Extracted English Intent: [{english_intent}]")
    
    # 3. Send the English text to the HR system
    agent_response = dispatch_english_intent_to_hr_agent(english_intent)
    
    logger.info("--- WhatsApp Audio-to-Intent Pipeline Completed Successfully ---")
    return agent_response

if __name__ == "__main__":
    # Ensure our script doesn't crash during local testing due to missing API keys
    os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY", "dummy-key-for-testing")
    
    # Create a fake audio file to run a test
    dummy_wav_path = "whatsapp_test_audio.ogg"
    
    try:
        with open(dummy_wav_path, "wb") as f:
            f.write(b"simulated_audio_data")
        logger.info(f"TEST SETUP: Created simulated audio file at {dummy_wav_path}")
        
        # Run the full pipeline process with the fake file
        final_result = process_whatsapp_audio_to_intent(dummy_wav_path)
        
        print("\n" + "="*60)
        print("FINAL PIPELINE RESULT:")
        print("="*60)
        if final_result:
            print(json.dumps(final_result, indent=4))
        else:
            print("STATUS: Pipeline stopped early due to expected test errors (e.g., fake API key).")
        print("="*60 + "\n")
        
    finally:
        # Clean up the fake file after the test
        if os.path.exists(dummy_wav_path):
            os.remove(dummy_wav_path)
            logger.info("TEST TEARDOWN: Cleaned up test file.")
