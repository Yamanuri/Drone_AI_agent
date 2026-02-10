# Python Backend - Quick Start (10 Minutes)

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│          Streamlit Frontend (app.py)            │
│     - Chat Interface                            │
│     - Dashboard with metrics                    │
│     - Data browser (pilots/drones/missions)     │
└─────────────────┬───────────────────────────────┘
                  │ HTTP Requests (port 8501)
                  │
┌─────────────────▼───────────────────────────────┐
│       FastAPI Backend (main.py)                 │
│     - /chat → CoordinatorAgent (OpenAI)         │
│     - /assign → ConflictEngine rules            │
│     - /conflicts/check → Rule detection         │
│     - /sync → Google Sheets integration         │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│     Data & Services Layer                       │
│   ├─ DataManager (CSV + Google Sheets)          │
│   ├─ ConflictEngine (rule-based)                │
│   ├─ CoordinatorAgent (OpenAI)                  │
│   └─ Models (Pydantic validation)               │
└─────────────────┬───────────────────────────────┘
                  │
┌─────────────────▼───────────────────────────────┐
│    Data Sources                                 │
│   ├─ CSV files (pilot_roster, drone_fleet, etc) │
│   ├─ Google Sheets (optional 2-way sync)        │
│   └─ OpenAI API (for conversation)              │
└─────────────────────────────────────────────────┘
```

---

## Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **pip** (comes with Python)
- **OpenAI API Key** ([Get free tier](https://platform.openai.com)) - OR use rule-based mode (free)

---

## STEP 1: Install Python Dependencies

```bash
cd c:\Users\PC\Documents\assignment_drone\drone-coordinator-backend

pip install -r requirements.txt
```

**What it installs:**
- `fastapi` - Fast backend API framework
- `uvicorn` - ASGI server for FastAPI
- `streamlit` - Simple UI framework
- `pandas` - CSV/data processing
- `openai` - OpenAI API client
- `python-dotenv` - Environment variables

---

## STEP 2: Create Environment File

Copy `.env.example` to `.env` and fill in your config:

```bash
# Windows:
copy .env.example .env

# Then edit .env with your settings
```

**Minimal .env (rule-based, no OpenAI):**
```
OPENAI_API_KEY=none
PILOTS_CSV_PATH=./data/pilot_roster.csv
DRONES_CSV_PATH=./data/drone_fleet.csv
MISSIONS_CSV_PATH=./data/missions.csv
API_HOST=127.0.0.1
API_PORT=8000
```

**With OpenAI (recommended):**
```
OPENAI_API_KEY=sk-your-actual-key-here
PILOTS_CSV_PATH=./data/pilot_roster.csv
DRONES_CSV_PATH=./data/drone_fleet.csv
MISSIONS_CSV_PATH=./data/missions.csv
```

---

## STEP 3: Start FastAPI Backend

```bash
python main.py
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 [Press CTRL+C to quit]
```

✅ Backend is now running at http://127.0.0.1:8000

**Keep this terminal open** and open a NEW terminal for the next step.

---

## STEP 4: Start Streamlit Frontend (NEW TERMINAL)

```bash
cd c:\Users\PC\Documents\assignment_drone\drone-coordinator-backend

streamlit run app.py
```

**Expected output:**
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
```

✅ Frontend is now running at http://localhost:8501

---

## STEP 5: Open Web Browser

Open your browser and go to:
```
http://localhost:8501
```

You should see the **Drone Operations Coordinator** interface with:
- ✅ Chat Agent tab
- ✅ Operations Dashboard
- ✅ Pilot Roster viewer
- ✅ Drone Fleet viewer
- ✅ Mission browser
- ✅ Conflict detector

---

## Test It Out

### In the Chat Agent:
```
User: "Show available pilots"
Agent: Lists all pilots with status "Available"

User: "What are the conflicts?"
Agent: Identifies location mismatches, skill gaps, etc.

User: "Assign mission PRJ001"
Agent: Suggests best pilot-drone pairing with feasibility score
```

### On Dashboard:
- See real-time metrics (total pilots, drones, missions)
- View availability counts
- Check last sync time

### On Pilots/Drones/Missions:
- Browse full roster in tables
- Filter by availability
- Propose assignments for missions

---

## API Endpoints (Testing with Curl/Postman)

```bash
# Health check
curl http://127.0.0.1:8000/health

# Get all pilots
curl http://127.0.0.1:8000/pilots

# Get available drones
curl http://127.0.0.1:8000/drones/available

# Chat with agent
curl -X POST http://127.0.0.1:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"content":"show available pilots"}'

# Check conflicts
curl http://127.0.0.1:8000/conflicts/check

# Propose assignment
curl -X POST http://127.0.0.1:8000/assign?mission_id=PRJ001
```

---

## Project Structure

```
drone-coordinator-backend/
├── main.py                          ← FastAPI app (port 8000)
├── app.py                           ← Streamlit app (port 8501)
├── models.py                        ← Pydantic data models
├── requirements.txt                 ← Dependencies
├── .env.example                     ← Config template
├── .env                             ← Your actual config (create this)
├── services/
│   ├── __init__.py
│   ├── data_manager.py              ← CSV + Google Sheets loader
│   ├── conflict_engine.py           ← Rule-based conflict detection
│   └── coordinator_agent.py         ← OpenAI integration
└── data/
    ├── pilot_roster.csv             ← Sample pilot data
    ├── drone_fleet.csv              ← Sample drone data
    └── missions.csv                 ← Sample mission data
```

---

## File Descriptions

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application - REST API backend |
| `app.py` | Streamlit frontend - Web UI |
| `models.py` | Pydantic models for validation |
| `services/data_manager.py` | Loads CSV files, manages data |
| `services/conflict_engine.py` | 7 rule-based conflict checks |
| `services/coordinator_agent.py` | OpenAI chat or rule-based responses |
| `data/*.csv` | Sample pilot, drone, mission data |

---

## OpenAI Integration

### Without OpenAI (Free, Rule-Based):
- Chat uses hardcoded responses
- No natural language understanding
- Fast and deterministic
- Set `OPENAI_API_KEY=none` in .env

### With OpenAI (Requires API Key):
- Chat uses GPT-3.5-turbo
- Understands natural language queries
- Generates contextual responses
- Set `OPENAI_API_KEY=sk-your-key` in .env

**Get Free OpenAI Credits:**
1. Go to https://platform.openai.com/signup
2. Sign up for free account
3. Go to API keys → Create new secret key
4. Add to .env: `OPENAI_API_KEY=sk-...`

---

## Troubleshooting

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
**Fix:**
```bash
pip install -r requirements.txt
```

### ❌ "Address already in use" port 8000
**Fix:** FastAPI already running
```bash
# Find and kill the process using port 8000
# Or use different port:
python -m uvicorn main:app --host 127.0.0.1 --port 8001
```

### ❌ "Address already in use" port 8501
**Fix:** Streamlit already running
```bash
streamlit run app.py --server.port 8502
```

### ❌ CSV file not found
**Fix:** Check paths in `.env`
```
PILOTS_CSV_PATH=./data/pilot_roster.csv
```

### ❌ OpenAI API error "invalid_request_error"
**Fix:** 
- Check API key is correct: `OPENAI_API_KEY=sk-...`
- Ensure you have free credits or paid plan
- Restart app after changing .env

### ❌ Streamlit says "API connection error"
**Fix:** Make sure FastAPI is running in another terminal
```bash
# Terminal 1: python main.py
# Terminal 2: streamlit run app.py
```

---

## Features Implemented

✅ **Rule-Based Conflict Detection**
- Skill matching
- Certification validation
- Location compatibility
- Availability checking
- Drone maintenance status
- Capability matching
- Feasibility scoring (0-100%)

✅ **AI Chat Agent**
- OpenAI GPT-3.5-turbo integration
- Natural language queries
- Context-aware responses
- Fallback to rule-based mode if no API key

✅ **Data Management**
- Load CSV files (pilots, drones, missions)
- Parse data into Pydantic models
- Google Sheets sync (placeholder for API implementation)
- Real-time filtering and queries

✅ **REST API**
- Health checks
- Operational status
- Data endpoints (pilots, drones, missions)
- Assignment proposal endpoint
- Conflict detection endpoint
- Chat endpoint

✅ **Streamlit UI**
- 6 pages (Chat, Dashboard, Pilots, Drones, Missions, Conflicts)
- Real-time data display
- Assignment proposal tool
- Conflict browser
- Responsive design

---

## Next Steps

1. ✅ **Running locally** - You're here!
2. **Deploy to cloud** - Heroku, Railway, Fly.io
3. **Google Sheets sync** - Implement 2-way sync for data
4. **Advanced analytics** - Pilot performance, mission success rates
5. **Notifications** - Alert on conflicts, urgent missions
6. **Multi-language** - Spanish, French, Mandarin support

---

## Deployment Options

### Heroku (Free tier available)
```bash
heroku create your-app-name
heroku config:set OPENAI_API_KEY=sk-...
git push heroku main
```

### Railway.app (Simple)
1. Connect GitHub repo
2. Add environment variables
3. Deploy with one click

### Fly.io
```bash
fly auth login
fly launch
fly deploy
```

---

## API Documentation

Once running, visit: `http://127.0.0.1:8000/docs`
(Interactive Swagger UI for all endpoints)

---

## Support

- **Code issues?** Check console logs in both terminals
- **CSV parsing?** Look at `services/data_manager.py`
- **API errors?** Visit http://127.0.0.1:8000/docs for endpoint details
- **Streamlit problems?** Check http://localhost:8501 console (press 'c' in terminal)

---

**Last Updated:** February 10, 2026
