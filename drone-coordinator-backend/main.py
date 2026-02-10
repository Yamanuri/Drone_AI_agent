"""
Drone Operations Coordinator Backend
FastAPI + OpenAI + Google Sheets Integration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import List, Optional

# Import services
from services.coordinator_agent import CoordinatorAgent
from services.data_manager import DataManager
from services.conflict_engine import ConflictEngine
from models import (
    PilotData, DroneData, MissionData, 
    AssignmentProposal, ChatMessage, ChatResponse
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Drone Operations Coordinator API",
    description="AI-powered drone fleet management system",
    version="1.0.0"
)

# Add CORS middleware for Streamlit communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
data_manager = DataManager()
conflict_engine = ConflictEngine()
coordinator_agent = CoordinatorAgent()

# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health")
def health_check():
    """API health status."""
    return {
        "status": "healthy",
        "service": "Drone Operations Coordinator",
        "version": "1.0.0"
    }

@app.get("/status")
def get_status():
    """Get current operational status."""
    try:
        pilots = data_manager.get_pilots()
        drones = data_manager.get_drones()
        missions = data_manager.get_missions()
        
        available_pilots = [p for p in pilots if p.status == "Available"]
        available_drones = [d for d in drones if d.status == "Available"]
        
        return {
            "total_pilots": len(pilots),
            "available_pilots": len(available_pilots),
            "total_drones": len(drones),
            "available_drones": len(available_drones),
            "total_missions": len(missions),
            "last_sync": data_manager.last_sync_time,
            "data_source": "google_sheets" if data_manager.last_sync_time else "csv_fallback"
        }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# DATA ENDPOINTS
# ============================================================================

@app.get("/pilots", response_model=List[PilotData])
def get_all_pilots():
    """Get all pilots."""
    try:
        return data_manager.get_pilots()
    except Exception as e:
        logger.error(f"Failed to get pilots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/drones", response_model=List[DroneData])
def get_all_drones():
    """Get all drones."""
    try:
        return data_manager.get_drones()
    except Exception as e:
        logger.error(f"Failed to get drones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/missions", response_model=List[MissionData])
def get_all_missions():
    """Get all missions."""
    try:
        return data_manager.get_missions()
    except Exception as e:
        logger.error(f"Failed to get missions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/pilots/available")
def get_available_pilots():
    """Get available pilots."""
    try:
        pilots = data_manager.get_pilots()
        return [p for p in pilots if p.status == "Available"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/drones/available")
def get_available_drones():
    """Get available drones."""
    try:
        drones = data_manager.get_drones()
        return [d for d in drones if d.status == "Available"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# ASSIGNMENT ENDPOINTS
# ============================================================================

@app.post("/assign", response_model=AssignmentProposal)
def propose_assignment(mission_id: str):
    """Propose best assignment for a mission."""
    try:
        mission = data_manager.get_mission_by_id(mission_id)
        if not mission:
            raise HTTPException(status_code=404, detail="Mission not found")
        
        pilots = data_manager.get_pilots()
        drones = data_manager.get_drones()
        
        # Find best assignment
        best_assignment = conflict_engine.find_best_assignment(mission, pilots, drones)
        
        if not best_assignment:
            raise HTTPException(status_code=400, detail="No suitable pilot-drone pairing found")
        
        return best_assignment
    except Exception as e:
        logger.error(f"Assignment proposal failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conflicts/check")
def check_conflicts():
    """Check for scheduling and capability conflicts."""
    try:
        pilots = data_manager.get_pilots()
        drones = data_manager.get_drones()
        missions = data_manager.get_missions()
        
        conflicts = conflict_engine.detect_all_conflicts(pilots, drones, missions)
        return {"total_conflicts": len(conflicts), "conflicts": conflicts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHAT/AI AGENT ENDPOINTS
# ============================================================================

@app.post("/chat", response_model=ChatResponse)
def chat_with_agent(message: ChatMessage):
    """Send message to AI coordinator agent."""
    try:
        # Load current data context
        pilots = data_manager.get_pilots()
        drones = data_manager.get_drones()
        missions = data_manager.get_missions()
        
        # Get response from OpenAI
        response = coordinator_agent.process_query(
            user_message=message.content,
            pilots=pilots,
            drones=drones,
            missions=missions
        )
        
        return ChatResponse(
            message=response,
            timestamp=coordinator_agent.get_timestamp()
        )
    except Exception as e:
        logger.error(f"Chat processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# SYNC ENDPOINTS
# ============================================================================

@app.post("/sync/google-sheets")
def sync_from_google_sheets():
    """Force sync from Google Sheets."""
    try:
        result = data_manager.sync_from_google_sheets()
        return {
            "status": "success",
            "message": "Data synced from Google Sheets",
            "result": result
        }
    except Exception as e:
        logger.error(f"Google Sheets sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Google Sheets sync failed: {str(e)}")

@app.post("/sync/to-google-sheets")
def sync_to_google_sheets():
    """Sync local changes back to Google Sheets."""
    try:
        result = data_manager.sync_to_google_sheets()
        return {
            "status": "success",
            "message": "Data synced to Google Sheets",
            "result": result
        }
    except Exception as e:
        logger.error(f"Google Sheets write sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Google Sheets write sync failed: {str(e)}")

# ============================================================================
# RUN APPLICATION
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
