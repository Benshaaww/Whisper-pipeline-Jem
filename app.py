import streamlit as st
import tempfile
import os
from openai import OpenAI, APIError

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Jem HR: Voice PoC",
    page_icon="🎙️",
    layout="centered"
)

# --- HEADER & CONTEXT ---
st.title("🎙️ Jem HR: Voice-to-Intent PoC")
st.markdown("""
**Purpose:** Overcoming literacy and language barriers for deskless, frontline workers in South Africa.

This tool allows a worker to record a native-language voice note (e.g., in isiZulu, Sesotho, or Afrikaans). 
The audio is transcribed and translated into English using OpenAI Whisper, then routed to a simulated ReAct agent for HR processing.
""")
st.divider()

# --- INITIALIZE OPENAI CLIENT ---
# Security Requirement: Use st.secrets strictly. Do not use os.getenv() for Streamlit Community Cloud.
try:
    openai_api_key = st.secrets["OPENAI_API_KEY"]
    client = OpenAI(api_key=openai_api_key)
except KeyError:
    st.error("🚨 Configuration Error: `OPENAI_API_KEY` not found in Streamlit secrets.")
    st.stop()
except Exception as e:
    st.error(f"🚨 Failed to initialize OpenAI client: {e}")
    st.stop()

# --- AUDIO INPUT ---
st.subheader("1. Record a Voice Note")
# Streamlit's native audio input widget (works on mobile/desktops)
audio_value = st.audio_input("Tap the microphone to record your request:")

if audio_value is not None:
    st.success("✅ Audio captured successfully!")
    
    # --- PROCESSING ---
    st.subheader("2. AI Processing Pipeline")
    
    with st.spinner("Translating audio to English..."):
        # The hard part: Handle the Streamlit BytesIO buffer
        # We must write the buffer to a physical temporary file so the OpenAI SDK can read it
        try:
            # Create a temporary file with a supported audio extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_value.read())
                tmp_file_path = tmp_file.name
                
            # Call the Whisper Translations endpoint (always outputs English)
            with open(tmp_file_path, "rb") as audio_file:
                response = client.audio.translations.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                
            english_intent = str(response).strip()
            
            # Clean up the temporary file immediately after use
            os.remove(tmp_file_path)
            
        except APIError as e:
            st.error(f"❌ OpenAI API Error: {e}")
            st.stop()
        except Exception as e:
            st.error(f"❌ Unexpected Error during processing: {e}")
            
            # Ensure cleanup even on failure
            if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)
            st.stop()

    # --- RESULTS: TRANSLATION ---
    st.success("Translation Complete!")
    st.info(f"**Extracted English Intent:**\n\n\"{english_intent}\"")
    
    # --- AGENT SIMULATION ---
    st.subheader("3. HR Agent Routing Simulation")
    
    with st.spinner("Agent thinking..."):
        # A simple if/elif/else router simulating ReAct agent logic based on the intent string
        intent_lower = english_intent.lower()
        
        if any(word in intent_lower for word in ["advance", "pay", "money", "salary", "wage"]):
            tool_selected = "initiate_earned_wage_access"
            agent_response = "I see you are asking about your pay or a cash advance. I am launching the wage access tool."
            
        elif any(word in intent_lower for word in ["leave", "holiday", "sick", "off", "vacation"]):
            tool_selected = "query_leave_balance"
            agent_response = "I see you are asking about time off. I am checking your current leave balances."
            
        elif any(word in intent_lower for word in ["grievance", "complain", "fight", "manager", "unsafe"]):
            tool_selected = "log_hr_grievance"
            agent_response = "I am sorry to hear there is an issue. I am opening a confidential HR grievance ticket for you."
            
        else:
            tool_selected = "general_faq_search"
            agent_response = "I did not recognize a specific HR workflow. Checking the general employee handbook for answers."

        # Display the Agent's reasoning trace
        st.write("🤖 **ReAct Agent Trace:**")
        st.code(f"""
[Input]: "{english_intent}"
[Thought]: Need to determine the HR domain for this request.
[Action]: Selecting routing tool...
[Tool Selected]: {tool_selected}
[Output]: {agent_response}
        """, language="markdown")
        
        st.success("✅ Pipeline execution complete!")
