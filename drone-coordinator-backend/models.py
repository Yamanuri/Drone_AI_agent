"""
Pydantic models for data validation and API responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum

# ============================================================================
# ENUMS
# ============================================================================

class PilotStatus(str, Enum):
    AVAILABLE = "Available"
    ASSIGNED = "Assigned"
    ON_LEAVE = "On Leave"

class DroneStatus(str, Enum):
    AVAILABLE = "Available"
    MAINTENANCE = "Maintenance"
    IN_USE = "In Use"

class MissionPriority(str, Enum):
    STANDARD = "Standard"
    HIGH = "High"
    URGENT = "Urgent"

class ConflictSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

# ============================================================================
# DATA MODELS
# ============================================================================

class PilotData(BaseModel):
    """Pilot roster entry."""
    pilot_id: str = Field(..., description="Unique pilot identifier")
    name: str = Field(..., description="Full name of pilot")
    skills: List[str] = Field(default_factory=list, description="List of pilot skills")
    certifications: List[str] = Field(default_factory=list, description="Pilot certifications")
    location: str = Field(..., description="Current location")
    status: PilotStatus = Field(default=PilotStatus.AVAILABLE)
    current_assignment: Optional[str] = Field(None, description="Current mission ID")
    available_from: str = Field(..., description="Date pilot available")

    class Config:
        use_enum_values = True

class DroneData(BaseModel):
    """Drone fleet entry."""
    drone_id: str = Field(..., description="Unique drone identifier")
    model: str = Field(..., description="Drone model name")
    capabilities: List[str] = Field(default_factory=list, description="Drone capabilities (RGB, Thermal, LiDAR)") 
    status: DroneStatus = Field(default=DroneStatus.AVAILABLE)
    location: str = Field(..., description="Current location")
    current_assignment: Optional[str] = Field(None, description="Current mission ID")
    maintenance_due: str = Field(..., description="Next maintenance due date")

    class Config:
        use_enum_values = True

class MissionData(BaseModel):
    """Mission/project entry."""
    project_id: str = Field(..., description="Unique mission identifier")
    client: str = Field(..., description="Client name")
    location: str = Field(..., description="Mission location")
    required_skills: List[str] = Field(default_factory=list, description="Required skills")
    required_certs: List[str] = Field(default_factory=list, description="Required certifications")
    start_date: str = Field(..., description="Mission start date")
    end_date: str = Field(..., description="Mission end date")
    priority: MissionPriority = Field(default=MissionPriority.STANDARD)

    class Config:
        use_enum_values = True

# ============================================================================
# CONFLICT & ASSIGNMENT MODELS
# ============================================================================

class ConflictCheck(BaseModel):
    """Individual conflict check result."""
    check_type: str = Field(..., description="Type of conflict check")
    severity: ConflictSeverity = Field(...)
    message: str = Field(..., description="Detailed conflict message")
    resolved: bool = Field(default=False)

class AssignmentProposal(BaseModel):
    """Proposed pilot-drone assignment for a mission."""
    mission: MissionData
    pilot: PilotData
    drone: DroneData
    conflicts: List[ConflictCheck] = Field(default_factory=list)
    feasibility_score: float = Field(..., description="Assignment feasibility 0-100%")
    reasoning: str = Field(..., description="Why this assignment was proposed")

class ConflictDetectionResult(BaseModel):
    """Result of conflict detection."""
    conflict_id: str
    description: str
    severity: ConflictSeverity
    affected_items: List[str]
    recommendation: str

# ============================================================================
# CHAT/AGENT MODELS
# ============================================================================

class ChatMessage(BaseModel):
    """User message to coordinator agent."""
    content: str = Field(..., description="User query text")
    user_id: Optional[str] = Field(None, description="User identifier")
    timestamp: Optional[str] = Field(None, description="Message timestamp")

class ChatResponse(BaseModel):
    """Response from coordinator agent."""
    message: str = Field(..., description="Agent response text")
    timestamp: str = Field(..., description="Response timestamp")
    confidence: Optional[float] = Field(None, description="Agent confidence 0-1")
    action_taken: Optional[str] = Field(None, description="Action performed")

# ============================================================================
# SYNC MODELS
# ============================================================================

class SyncResult(BaseModel):
    """Result of data synchronization."""
    status: str = Field(..., description="sync status (success/failure)")
    records_synced: int = Field(..., description="Number of records synced")
    timestamp: str = Field(..., description="Sync timestamp")
    details: Optional[dict] = Field(None)

class DataStats(BaseModel):
    """Data statistics."""
    total_pilots: int
    available_pilots: int
    total_drones: int
    available_drones: int
    total_missions: int
    active_missions: int
    last_sync: str
