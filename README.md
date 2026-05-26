# AutonomousSalesEngineer
Technical sales consultant that turns a high-level requirements brief into a complete, valid, and quoted solution by navigating a product catalog, checking compatibility, staying within budget, and matching delivery constraints.

---

## System Requirements

| Requirement | Version |
|---|---|
| Python | 3.10 or higher |
| pip | Latest recommended |
| Operating System | Windows 10+, macOS 12+, or Ubuntu 20.04+ |
| Internet connection | Required (for Gemini API and Tavily search) |

---

## Dependencies

All dependencies are listed in `requirements.txt`. Key libraries:

| Library | Purpose |
|---|---|
| `google-genai` | Gemini 3.1 Flash LLM Lite and tool calling |
| `tavily-python` | Web search for real product results |
| `fpdf2` | PDF quote generation |
| `streamlit` | Web UI |
| `python-dotenv` | Load API keys from `.env` file |

---

## API Keys Required

You will need two free API keys before running this project:

| Key | Where to get it |
|---|---|
| `GEMINI_API_KEY` | https://aistudio.google.com → Get API Key |
| `TAVILY_API_KEY` | https://tavily.com → Sign up |

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/THAMWUTONG/AutonomousSalesEngineer
cd AutonomousSalesEngineer
```

### 2. Create a virtual environment (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API keys

Copy the example environment file:

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Open `.env` in any text editor and paste your API keys:

```
GEMINI_API_KEY=paste_your_gemini_key_here
TAVILY_API_KEY=paste_your_tavily_key_here
```

## Running the Application

```bash
streamlit run app.py
```

Then open your browser at `http://localhost:8501`

Type a brief into the text box, click **Generate Quote**, and wait 30–60 seconds for the agent to complete. A PDF download button will appear when done.

---

## Troubleshooting

**`ModuleNotFoundError`**
→ Make sure your virtual environment is activated and you ran `pip install -r requirements.txt`

**`GEMINI_API_KEY not found`**
→ Make sure your `.env` file exists and contains your key. Do not add quotes around the key value.

**`503 UNAVAILABLE` from Gemini**
→ The free tier is experiencing high demand. The agent has automatic retry logic built in — wait a moment and try again.

**Streamlit doesn't open automatically**
→ Manually open `http://localhost:8501` in your browser.

---
