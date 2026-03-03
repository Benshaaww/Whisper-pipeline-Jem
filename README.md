# JEM HR - Voice-to-Intent Pipeline PoC

This repository contains the Proof of Concept (PoC) for a WhatsApp-based HR platform designed for deskless and frontline workers manually or through an interactive UI. The pipeline ingests native-language voice notes (e.g., isiZulu, Sesotho, Afrikaans), transcribes and translates them into English using OpenAI's Whisper API, and routes the normalized English intent to a simulated ReAct agent for HR processing.

This project now includes three main ways to interact with the pipeline:
1. **Local CLI Testing** (`main.py`)
2. **Live REST API** (`api.py` via FastAPI)
3. **Web UI** (`app.py` via Streamlit)

---

## 🚀 Quickstart: Streamlit Web UI
The easiest way to test the pipeline is using the Streamlit Web UI.

**1. Install Requirements:**
```bash
pip install -r requirements.txt
```

**2. Set your OpenAI API Key:**
Create a folder named `.streamlit` in the root of the project, and inside it, create a file named `secrets.toml`:
```toml
OPENAI_API_KEY="sk-your-real-api-key-here"
```

**3. Run the App:**
```bash
streamlit run app.py
```
*This will open a browser window where you can record audio directly from your microphone and see the HR agent's response.*

---

## ⚙️ Running the REST API (FastAPI)
You can run the pipeline as a live web server to accept HTTP `POST` requests containing audio files.

**1. Set Environment Variable:**
* **Windows (PowerShell):** `$env:OPENAI_API_KEY="sk-your-real-api-key-here"`
* **macOS/Linux:** `export OPENAI_API_KEY="sk-your-real-api-key-here"`

**2. Start the Server:**
```bash
uvicorn api:app --reload
```

**3. Test the Endpoint:**
Open a new terminal window and run:
```bash
python test_api.py
```
*This script will generate a dummy audio file, post it to `http://localhost:8000/process-audio/`, and print the JSON response.*

---

## 🖥️ Running the Core Logic CLI
If you just want to run the raw Python script to test the failure resilience handling:

```bash
python main.py
```

---

## 📦 Deployment to Streamlit Community Cloud
1. Push this repository to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) and click "New app".
3. Select this repository and point the main file path to `app.py`.
4. Click **Advanced Settings** and paste your API key into the Secrets box: `OPENAI_API_KEY="sk-..."`
5. Click **Deploy**.
