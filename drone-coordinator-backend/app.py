"""
Streamlit frontend for Drone Operations Coordinator
Run with: streamlit run app.py
"""

import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime
import logging

# Configure page
st.set_page_config(
    page_title="Drone Operations Coordinator",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# API configuration
API_URL = "http://127.0.0.1:8000"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "api_connected" not in st.session_state:
    st.session_state.api_connected = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def check_api_health():
    """Check if API is running."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False

def get_operational_status():
    """Fetch operational status from API."""
    try:
        response = requests.get(f"{API_URL}/status", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get status: {e}")
    return None

def get_pilots():
    """Fetch all pilots from API."""
    try:
        response = requests.get(f"{API_URL}/pilots", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get pilots: {e}")
    return []

def get_drones():
    """Fetch all drones from API."""
    try:
        response = requests.get(f"{API_URL}/drones", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get drones: {e}")
    return []

def get_missions():
    """Fetch all missions from API."""
    try:
        response = requests.get(f"{API_URL}/missions", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get missions: {e}")
    return []

def get_available_pilots():
    """Fetch available pilots."""
    try:
        response = requests.get(f"{API_URL}/pilots/available", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get available pilots: {e}")
    return []

def get_available_drones():
    """Fetch available drones."""
    try:
        response = requests.get(f"{API_URL}/drones/available", timeout=5)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Failed to get available drones: {e}")
    return []

def send_chat_message(message: str) -> str:
    """Send message to chat API and get response."""
    try:
        response = requests.post(
            f"{API_URL}/chat",
            json={"content": message, "timestamp": datetime.now().isoformat()},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return data.get("message", "No response from agent")
    except Exception as e:
        logger.error(f"Chat API error: {e}")
        return f"Error communicating with agent: {str(e)}"
    return "API error"

def propose_assignment(mission_id: str):
    """Propose assignment for mission."""
    try:
        response = requests.post(
            f"{API_URL}/assign?mission_id={mission_id}",
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Assignment error: {e}")
    return None

def check_conflicts():
    """Check for system conflicts."""
    try:
        response = requests.get(f"{API_URL}/conflicts/check", timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        logger.error(f"Conflict check error: {e}")
    return {"conflicts": []}

# ============================================================================
# PAGE HEADER
# ============================================================================

st.title("🚁 Drone Operations Coordinator")
st.markdown("**AI-powered fleet management system for Skylark Drones**")

# Check API connection
st.session_state.api_connected = check_api_health()

if not st.session_state.api_connected:
    st.error(
        """❌ **API Not Connected**
        
FastAPI server is not running. Start it with:
```bash
python main.py
```

The server should be running at http://127.0.0.1:8000"""
    )
else:
    st.success("✅ API Connected")

# ============================================================================
# SIDEBAR - NAVIGATION
# ============================================================================

with st.sidebar:
    st.header("📋 Navigation")
    
    page = st.radio(
        "Select Page",
        ["Chat Agent", "Dashboard", "Pilots", "Drones", "Missions", "Conflicts"]
    )
    
    st.divider()
    
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()
    
    if st.button("🔄 Sync from Google Sheets", use_container_width=True):
        try:
            response = requests.post(f"{API_URL}/sync/google-sheets", timeout=10)
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Synced from Google Sheets: {result.get('message', '')}")
                st.rerun()
            else:
                st.error(f"❌ Sync failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Sync error: {str(e)}")
    
    if st.button("📤 Sync to Google Sheets", use_container_width=True):
        try:
            response = requests.post(f"{API_URL}/sync/to-google-sheets", timeout=10)
            if response.status_code == 200:
                result = response.json()
                st.success(f"✅ Synced to Google Sheets: {result.get('message', '')}")
            else:
                st.error(f"❌ Sync failed: {response.status_code}")
        except Exception as e:
            st.error(f"❌ Sync error: {str(e)}")

# ============================================================================
# PAGE: CHAT AGENT
# ============================================================================

if page == "Chat Agent":
    st.header("💬 AI Coordinator Agent")
    st.markdown("Ask me anything about assignments, availability, or conflicts!")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if user_input := st.chat_input("Ask me about pilot assignments, drone status, etc..."):
        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Display user message
        with st.chat_message("user"):
            st.write(user_input)
        
        # Get agent response
        with st.spinner("🤖 Coordinator thinking..."):
            response = send_chat_message(user_input)
        
        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Display assistant message
        with st.chat_message("assistant"):
            st.write(response)

# ============================================================================
# PAGE: DASHBOARD
# ============================================================================

elif page == "Dashboard":
    st.header("📊 Operations Dashboard")
    
    status = get_operational_status()
    
    if status:
        # Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pilots", status.get("total_pilots", 0))
        
        with col2:
            st.metric("Available Pilots", status.get("available_pilots", 0))
        
        with col3:
            st.metric("Total Drones", status.get("total_drones", 0))
        
        with col4:
            st.metric("Available Drones", status.get("available_drones", 0))
        
        st.divider()
        
        # Recent activity
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("📍 Missions")
            st.metric("Total Missions", status.get("total_missions", 0))
        
        with col_right:
            st.subheader("🕐 Last Sync")
            st.text(status.get("last_sync", "Never"))

# ============================================================================
# PAGE: PILOTS
# ============================================================================

elif page == "Pilots":
    st.header("👨‍✈️ Pilot Roster")
    
    tab1, tab2 = st.tabs(["All Pilots", "Available Only"])
    
    with tab1:
        pilots = get_pilots()
        if pilots:
            # Convert to DataFrame
            df = pd.DataFrame([{
                "ID": p.get("pilot_id"),
                "Name": p.get("name"),
                "Skills": ", ".join(p.get("skills", [])),
                "Certifications": ", ".join(p.get("certifications", [])),
                "Location": p.get("location"),
                "Status": p.get("status"),
                "Current Assignment": p.get("current_assignment", "None")
            } for p in pilots])
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No pilot data available")
    
    with tab2:
        available = get_available_pilots()
        if available:
            df = pd.DataFrame([{
                "Name": p.get("name"),
                "Skills": ", ".join(p.get("skills", [])),
                "Location": p.get("location"),
                "Available From": p.get("available_from")
            } for p in available])
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No available pilots")

# ============================================================================
# PAGE: DRONES
# ============================================================================

elif page == "Drones":
    st.header("🚁 Drone Fleet")
    
    tab1, tab2 = st.tabs(["All Drones", "Available Only"])
    
    with tab1:
        drones = get_drones()
        if drones:
            df = pd.DataFrame([{
                "ID": d.get("drone_id"),
                "Model": d.get("model"),
                "Capabilities": ", ".join(d.get("capabilities", [])),
                "Status": d.get("status"),
                "Location": d.get("location"),
                "Current Assignment": d.get("current_assignment", "None"),
                "Maintenance Due": d.get("maintenance_due")
            } for d in drones])
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No drone data available")
    
    with tab2:
        available = get_available_drones()
        if available:
            df = pd.DataFrame([{
                "Model": d.get("model"),
                "Capabilities": ", ".join(d.get("capabilities", [])),
                "Location": d.get("location"),
                "Maintenance Due": d.get("maintenance_due")
            } for d in available])
            
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No available drones")

# ============================================================================
# PAGE: MISSIONS
# ============================================================================

elif page == "Missions":
    st.header("📋 Missions")
    
    missions = get_missions()
    if missions:
        df = pd.DataFrame([{
            "ID": m.get("project_id"),
            "Client": m.get("client"),
            "Location": m.get("location"),
            "Required Skills": ", ".join(m.get("required_skills", [])),
            "Required Certs": ", ".join(m.get("required_certs", [])),
            "Start": m.get("start_date"),
            "End": m.get("end_date"),
            "Priority": m.get("priority")
        } for m in missions])
        
        st.dataframe(df, use_container_width=True)
        
        # Assignment helper
        st.divider()
        st.subheader("🎯 Propose Assignment")
        
        selected_mission = st.selectbox(
            "Select Mission",
            options=[m.get("project_id") for m in missions],
            format_func=lambda x: next((m.get("client") for m in missions if m.get("project_id") == x), x)
        )
        
        if st.button("Find Best Assignment"):
            with st.spinner("Finding best assignment..."):
                proposal = propose_assignment(selected_mission)
                if proposal:
                    st.success("✅ Assignment Found!")
                    st.write(f"**Pilot:** {proposal.get('pilot', {}).get('name')}")
                    st.write(f"**Drone:** {proposal.get('drone', {}).get('model')}")
                    st.write(f"**Feasibility:** {proposal.get('feasibility_score')}%")
                    st.write(f"**Reasoning:** {proposal.get('reasoning')}")
                else:
                    st.error("❌ No suitable assignment found")
    else:
        st.info("No mission data available")

# ============================================================================
# PAGE: CONFLICTS
# ============================================================================

elif page == "Conflicts":
    st.header("⚠️ Conflict Detection")
    
    if st.button("Check for Conflicts", use_container_width=True):
        with st.spinner("Scanning for conflicts..."):
            conflicts_data = check_conflicts()
            
            conflicts = conflicts_data.get("conflicts", [])
            
            if not conflicts:
                st.success("✅ No conflicts detected - fleet operating smoothly!")
            else:
                st.error(f"⚠️ **{len(conflicts)} conflict(s) detected**")
                
                for conflict in conflicts:
                    with st.expander(f"🔴 {conflict.get('description', 'Unknown conflict')}"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            severity = conflict.get('severity', 'medium').upper()
                            st.write(f"**Severity:** {severity}")
                        
                        with col2:
                            st.write(f"**Type:** {conflict.get('conflict_id')}")
                        
                        st.write(f"**Affected Items:** {', '.join(conflict.get('affected_items', []))}")
                        st.write(f"**Recommendation:** {conflict.get('recommendation', 'N/A')}")

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.caption("🚁 Drone Operations Coordinator v1.0 | Powered by OpenAI + FastAPI")
