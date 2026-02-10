## Skylark Drones – Drone Operations Coordinator Agent

This repository contains two implementations of the **Drone Operations Coordinator** assignment:

- **React + Supabase web agent** (folder: `project-bolt-sb1-rn1pldhz/project`)
- **Python FastAPI + Streamlit backend agent** (folder: `drone-coordinator-backend`)

Both are aligned with the brief in `Read me-assignment-ops-coordinator-agent (4).md`.

---

## 1. React + Supabase Agent (Recommended for hosted demo)

- **Folder**: `project-bolt-sb1-rn1pldhz/project`
- **Stack**: React, TypeScript, Vite, Tailwind, Supabase
- **What it provides**:
  - Chat-based coordinator UI
  - Roster management, drone inventory, assignment tracking
  - Conflict detection and urgent reassignment logic backed by Supabase tables

### How to run

1. **Open a terminal and go to the project folder**
   ```bash
   cd project-bolt-sb1-rn1pldhz/project
   ```
2. **Create `.env.local` with your Supabase credentials** (URL + anon key).  
   Details and exact commands are in `EXECUTION_STEPS.md` and `SETUP_GUIDE.md`.
3. **Run the SQL migrations in Supabase** (create tables + sample data) from `supabase/migrations`.
4. **Install and start:**
   ```bash
   npm install
   npm run dev
   ```
5. Open `http://localhost:5173` in your browser and use the chat interface.

For deeper explanation of services, data model, and commands, see:
- `project-bolt-sb1-rn1pldhz/project/README.md`
- `project-bolt-sb1-rn1pldhz/project/EXECUTION_STEPS.md`
- `project-bolt-sb1-rn1pldhz/project/SETUP_GUIDE.md`

---

## 2. Python FastAPI + Streamlit Agent

- **Folder**: `drone-coordinator-backend`
- **Stack**: FastAPI, Streamlit, Pandas, Python
- **What it provides**:
  - REST API for pilots, drones, missions, assignments, conflicts, and chat
  - Streamlit UI (dashboard + chat)
  - CSV-backed data with a placeholder for Google Sheets sync

### How to run

1. **Open a terminal and go to the backend folder**
   ```bash
   cd drone-coordinator-backend
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
3. **Create `.env` from `.env.example` and adjust paths / optional API key**
4. **Start the backend (FastAPI)**
   ```bash
   python main.py
   ```
5. **Start the Streamlit UI in another terminal**
   ```bash
   streamlit run app.py
   ```
6. Open `http://localhost:8501` in your browser.

For more detail, see:
- `drone-coordinator-backend/README.md`
- `drone-coordinator-backend/QUICKSTART.md`

---

## Notes on the Assignment and Tooling

- The assignment description is in: `Read me-assignment-ops-coordinator-agent (4).md` and  
  `project-bolt-sb1-rn1pldhz/project/Read_me-assignment-ops-coordinator-agent_(4).md`.
- Some boilerplate (project scaffolding) was generated with AI tooling, but all domain logic
  (roster management, inventory, conflict detection, reassignment strategies, Supabase schema,
  and FastAPI/Streamlit wiring) has been reviewed and adapted specifically for this task.

