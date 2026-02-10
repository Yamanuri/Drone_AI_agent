"""
Conflict detection engine - rule-based system for identifying conflicts
"""

import logging
from typing import List, Optional
from datetime import datetime

from models import (
    PilotData, DroneData, MissionData,
    ConflictCheck, AssignmentProposal, ConflictDetectionResult
)

logger = logging.getLogger(__name__)

class ConflictEngine:
    """Rule-based conflict detection and assignment feasibility scoring."""
    
    def __init__(self, feasibility_threshold: float = 50):
        """Initialize conflict engine with threshold."""
        self.feasibility_threshold = feasibility_threshold
    
    # ========================================================================
    # INDIVIDUAL CONFLICT CHECKS
    # ========================================================================
    
    def check_skill_match(self, pilot: PilotData, mission: MissionData) -> ConflictCheck:
        """Check if pilot has required skills."""
        missing_skills = []
        for req_skill in mission.required_skills:
            has_skill = any(
                req_skill.lower() in s.lower() 
                for s in pilot.skills
            )
            if not has_skill:
                missing_skills.append(req_skill)
        
        if missing_skills:
            return ConflictCheck(
                check_type="skill_mismatch",
                severity="high",
                message=f"Pilot missing skills: {', '.join(missing_skills)}"
            )
        
        return ConflictCheck(
            check_type="skill_match",
            severity="low",
            message=f"All required skills present",
            resolved=True
        )
    
    def check_certifications(self, pilot: PilotData, mission: MissionData) -> ConflictCheck:
        """Check if pilot has required certifications."""
        missing_certs = []
        for req_cert in mission.required_certs:
            has_cert = any(
                req_cert.lower() in c.lower()
                for c in pilot.certifications
            )
            if not has_cert:
                missing_certs.append(req_cert)
        
        if missing_certs:
            return ConflictCheck(
                check_type="certification_mismatch",
                severity="high",
                message=f"Pilot missing certifications: {', '.join(missing_certs)}"
            )
        
        return ConflictCheck(
            check_type="certification_match",
            severity="low",
            message=f"All required certifications present",
            resolved=True
        )
    
    def check_location_match(self, pilot: PilotData, mission: MissionData) -> ConflictCheck:
        """Check if pilot location matches mission location."""
        if pilot.location.lower() != mission.location.lower():
            return ConflictCheck(
                check_type="location_mismatch",
                severity="medium",
                message=f"Location mismatch: {pilot.location} vs {mission.location}"
            )
        
        return ConflictCheck(
            check_type="location_match",
            severity="low",
            message=f"Location match: {pilot.location}",
            resolved=True
        )
    
    def check_pilot_availability(self, pilot: PilotData, mission: MissionData) -> ConflictCheck:
        """Check if pilot is available for mission dates."""
        if pilot.status != "Available":
            return ConflictCheck(
                check_type="pilot_unavailable",
                severity="high",
                message=f"Pilot status: {pilot.status}. Available from: {pilot.available_from}"
            )
        
        # Check if available_from date is before mission start
        try:
            available_date = datetime.strptime(pilot.available_from, "%Y-%m-%d")
            mission_start = datetime.strptime(mission.start_date, "%Y-%m-%d")
            
            if available_date > mission_start:
                return ConflictCheck(
                    check_type="availability_conflict",
                    severity="high",
                    message=f"Pilot available {pilot.available_from}, mission starts {mission.start_date}"
                )
        except ValueError:
            logger.warning("Date parsing failed - skipping date check")
        
        return ConflictCheck(
            check_type="availability_ok",
            severity="low",
            message=f"Pilot available",
            resolved=True
        )
    
    def check_drone_availability(self, drone: DroneData) -> ConflictCheck:
        """Check if drone is available."""
        if drone.status != "Available":
            return ConflictCheck(
                check_type="drone_unavailable",
                severity="high",
                message=f"Drone status: {drone.status}. Maintenance due: {drone.maintenance_due}"
            )
        
        return ConflictCheck(
            check_type="drone_available",
            severity="low",
            message=f"Drone available",
            resolved=True
        )
    
    def check_drone_capabilities(self, drone: DroneData, mission: MissionData) -> ConflictCheck:
        """Check if drone has required capabilities."""
        # Map mission skills to drone capabilities
        capability_keywords = ['Thermal', 'LiDAR', 'RGB', 'Hyperspectral', '4K']
        required_capabilities = []
        
        for skill in mission.required_skills:
            for keyword in capability_keywords:
                if keyword.lower() in skill.lower():
                    required_capabilities.append(keyword)
        
        if not required_capabilities:
            return ConflictCheck(
                check_type="capability_not_required",
                severity="low",
                message="No specific capabilities required",
                resolved=True
            )
        
        missing_capabilities = []
        for req_cap in required_capabilities:
            has_cap = any(
                req_cap.lower() in cap.lower()
                for cap in drone.capabilities
            )
            if not has_cap:
                missing_capabilities.append(req_cap)
        
        if missing_capabilities:
            return ConflictCheck(
                check_type="capability_mismatch",
                severity="high",
                message=f"Drone missing capabilities: {', '.join(missing_capabilities)}"
            )
        
        return ConflictCheck(
            check_type="capability_match",
            severity="low",
            message=f"Drone has required capabilities",
            resolved=True
        )
    
    def check_drone_location(self, drone: DroneData, mission: MissionData) -> ConflictCheck:
        """Check if drone location matches mission."""
        if drone.location.lower() != mission.location.lower():
            return ConflictCheck(
                check_type="drone_location_mismatch",
                severity="medium",
                message=f"Drone location mismatch: {drone.location} vs {mission.location}"
            )
        
        return ConflictCheck(
            check_type="drone_location_match",
            severity="low",
            message=f"Drone location match: {drone.location}",
            resolved=True
        )
    
    # ========================================================================
    # FEASIBILITY SCORING
    # ========================================================================
    
    def calculate_feasibility_score(self, conflicts: List[ConflictCheck]) -> float:
        """Calculate assignment feasibility score 0-100%."""
        if not conflicts:
            return 100.0
        
        # Severity penalties
        severity_penalties = {
            "low": 0,
            "medium": 15,
            "high": 40
        }
        
        total_penalty = 0
        critical_issues = 0
        
        for conflict in conflicts:
            if conflict.resolved:
                continue  # Don't penalize resolved conflicts
            
            penalty = severity_penalties.get(conflict.severity, 0)
            total_penalty += penalty
            
            if conflict.severity == "high":
                critical_issues += 1
        
        # Exponential penalty for multiple critical issues
        if critical_issues > 0:
            total_penalty += critical_issues * 20
        
        feasibility_score = max(0, 100 - total_penalty)
        return round(feasibility_score, 1)
    
    # ========================================================================
    # ASSIGNMENT PROPOSAL GENERATION
    # ========================================================================
    
    def propose_assignment(
        self, mission: MissionData, pilot: PilotData, drone: DroneData
    ) -> Optional[AssignmentProposal]:
        """Propose a single pilot-drone assignment for a mission."""
        conflicts = [
            self.check_skill_match(pilot, mission),
            self.check_certifications(pilot, mission),
            self.check_location_match(pilot, mission),
            self.check_pilot_availability(pilot, mission),
            self.check_drone_availability(drone),
            self.check_drone_capabilities(drone, mission),
            self.check_drone_location(drone, mission),
        ]
        
        feasibility = self.calculate_feasibility_score(conflicts)
        
        # Filter to unresolved conflicts only
        unresolved_conflicts = [c for c in conflicts if not c.resolved]
        
        # Generate reasoning
        reasoning_parts = []
        if feasibility >= self.feasibility_threshold:
            reasoning_parts.append(f"High feasibility assignment ({feasibility}%)")
        else:
            reasoning_parts.append(f"Low feasibility assignment ({feasibility}%)")
        
        if unresolved_conflicts:
            reasons_str = "; ".join([c.message for c in unresolved_conflicts])
            reasoning_parts.append(f"Issues: {reasons_str}")
        else:
            reasoning_parts.append("No major conflicts detected")
        
        reasoning = " | ".join(reasoning_parts)
        
        return AssignmentProposal(
            mission=mission,
            pilot=pilot,
            drone=drone,
            conflicts=unresolved_conflicts,
            feasibility_score=feasibility,
            reasoning=reasoning
        )
    
    def find_best_assignment(
        self, mission: MissionData, pilots: List[PilotData], drones: List[DroneData]
    ) -> Optional[AssignmentProposal]:
        """Find the best pilot-drone pairing for a mission."""
        proposals = []
        
        for pilot in pilots:
            for drone in drones:
                proposal = self.propose_assignment(mission, pilot, drone)
                if proposal and proposal.feasibility_score >= self.feasibility_threshold:
                    proposals.append(proposal)
        
        if not proposals:
            return None
        
        # Sort by feasibility score, descending
        proposals.sort(key=lambda x: x.feasibility_score, reverse=True)
        return proposals[0]
    
    def find_alternatives(
        self, mission: MissionData, pilots: List[PilotData], drones: List[DroneData],
        exclude_pilot_id: Optional[str] = None
    ) -> List[AssignmentProposal]:
        """Find alternative assignments for a mission."""
        proposals = []
        
        for pilot in pilots:
            if exclude_pilot_id and pilot.pilot_id == exclude_pilot_id:
                continue
            
            for drone in drones:
                proposal = self.propose_assignment(mission, pilot, drone)
                if proposal and proposal.feasibility_score >= self.feasibility_threshold:
                    proposals.append(proposal)
        
        # Sort by feasibility score
        proposals.sort(key=lambda x: x.feasibility_score, reverse=True)
        return proposals
    
    # ========================================================================
    # GLOBAL CONFLICT DETECTION
    # ========================================================================
    
    def detect_all_conflicts(
        self, pilots: List[PilotData], drones: List[DroneData], missions: List[MissionData]
    ) -> List[ConflictDetectionResult]:
        """Detect all conflicts across the entire system."""
        conflicts = []
        
        # Check for double-booked pilots
        for pilot in pilots:
            # Find all missions assigned to this pilot
            pilot_assignments = [
                m for m in missions
                if m.project_id == pilot.current_assignment
            ]
            
            # Check for date overlaps
            for i in range(len(pilot_assignments)):
                for j in range(i + 1, len(pilot_assignments)):
                    try:
                        start1 = datetime.strptime(pilot_assignments[i].start_date, "%Y-%m-%d")
                        end1 = datetime.strptime(pilot_assignments[i].end_date, "%Y-%m-%d")
                        start2 = datetime.strptime(pilot_assignments[j].start_date, "%Y-%m-%d")
                        end2 = datetime.strptime(pilot_assignments[j].end_date, "%Y-%m-%d")
                        
                        # Check if date ranges overlap
                        if start1 <= end2 and start2 <= end1:
                            conflicts.append(ConflictDetectionResult(
                                conflict_id=f"pilot_overlap_{pilot.pilot_id}",
                                description=f"Pilot {pilot.name} has overlapping assignments",
                                severity="high",
                                affected_items=[pilot.pilot_id, pilot_assignments[i].project_id, pilot_assignments[j].project_id],
                                recommendation=f"Reassign pilot {pilot.name} to avoid date conflict between {pilot_assignments[i].client} and {pilot_assignments[j].client}"
                            ))
                    except ValueError:
                        logger.warning(f"Date parsing failed for pilot {pilot.name}")
            
            # Check if pilot is assigned to a mission but status is not 'Assigned'
            if pilot.current_assignment and not pilot_assignments:
                conflicts.append(ConflictDetectionResult(
                    conflict_id=f"pilot_assignment_mismatch_{pilot.pilot_id}",
                    description=f"Pilot {pilot.name} has assignment but not in mission list",
                    severity="medium",
                    affected_items=[pilot.pilot_id, pilot.current_assignment],
                    recommendation=f"Update pilot assignment status"
                ))
        
        # Check for low feasibility assignments
        for mission in missions:
            best = self.find_best_assignment(mission, pilots, drones)
            if best and best.feasibility_score < 60:
                conflicts.append(ConflictDetectionResult(
                    conflict_id=f"low_feasibility_{mission.project_id}",
                    description=f"Mission {mission.client} has low feasibility assignment",
                    severity="medium",
                    affected_items=[mission.project_id],
                    recommendation=f"Consider reassignment or skill development"
                ))
            elif not best:
                conflicts.append(ConflictDetectionResult(
                    conflict_id=f"no_assignment_{mission.project_id}",
                    description=f"No suitable assignment found for {mission.client}",
                    severity="high",
                    affected_items=[mission.project_id],
                    recommendation=f"Urgent: hire additional staff or delay mission"
                ))
        
        # Check for double-booked drones
        for drone in drones:
            # Find all missions assigned to this drone
            drone_assignments = [
                m for m in missions
                if m.project_id == drone.current_assignment
            ]
            
            # Check for date overlaps
            for i in range(len(drone_assignments)):
                for j in range(i + 1, len(drone_assignments)):
                    try:
                        start1 = datetime.strptime(drone_assignments[i].start_date, "%Y-%m-%d")
                        end1 = datetime.strptime(drone_assignments[i].end_date, "%Y-%m-%d")
                        start2 = datetime.strptime(drone_assignments[j].start_date, "%Y-%m-%d")
                        end2 = datetime.strptime(drone_assignments[j].end_date, "%Y-%m-%d")
                        
                        # Check if date ranges overlap
                        if start1 <= end2 and start2 <= end1:
                            conflicts.append(ConflictDetectionResult(
                                conflict_id=f"drone_overlap_{drone.drone_id}",
                                description=f"Drone {drone.model} has overlapping assignments",
                                severity="high",
                                affected_items=[drone.drone_id, drone_assignments[i].project_id, drone_assignments[j].project_id],
                                recommendation=f"Reassign drone {drone.model} to avoid date conflict between {drone_assignments[i].client} and {drone_assignments[j].client}"
                            ))
                    except ValueError:
                        logger.warning(f"Date parsing failed for drone {drone.model}")
            
            # Check if drone is assigned to a mission but status is not 'Assigned'
            if drone.current_assignment and not drone_assignments:
                conflicts.append(ConflictDetectionResult(
                    conflict_id=f"drone_assignment_mismatch_{drone.drone_id}",
                    description=f"Drone {drone.model} has assignment but not in mission list",
                    severity="medium",
                    affected_items=[drone.drone_id, drone.current_assignment],
                    recommendation=f"Update drone assignment status"
                ))
        
        # Handle urgent reassignments
        urgent_reassignments = self.handle_urgent_reassignments(pilots, drones, missions, conflicts)
        conflicts.extend(urgent_reassignments)
        
        return conflicts
        
    def handle_urgent_reassignments(
        self, pilots: List[PilotData], drones: List[DroneData], missions: List[MissionData], 
        conflicts: List[ConflictDetectionResult]
    ) -> List[ConflictDetectionResult]:
        """Handle urgent reassignments based on detected conflicts and system state."""
        urgent_actions = []
            
        # Identify critical conflicts that require immediate reassignment
        critical_conflicts = [c for c in conflicts if c.severity == "high"]
            
        for conflict in critical_conflicts:
            # For pilot conflicts, suggest alternative pilots
            if "pilot" in conflict.conflict_id:
                # Find missions that are affected
                affected_mission_ids = [item for item in conflict.affected_items if item.startswith('PRJ')]
                for mission_id in affected_mission_ids:
                    mission = next((m for m in missions if m.project_id == mission_id), None)
                    if mission:
                        # Find alternative pilots
                        alternatives = self.find_alternatives(mission, pilots, drones)
                        if alternatives:
                            urgent_actions.append(ConflictDetectionResult(
                                conflict_id=f"urgent_reassign_pilot_{mission_id}",
                                description=f"URGENT: Alternative pilot available for {mission.client}",
                                severity="high",
                                affected_items=[mission_id],
                                recommendation=f"Immediately reassign to pilot {alternatives[0].pilot.name} with feasibility {alternatives[0].feasibility_score}%"
                            ))
                        else:
                            urgent_actions.append(ConflictDetectionResult(
                                conflict_id=f"urgent_no_pilot_{mission_id}",
                                description=f"URGENT: No alternative pilot available for {mission.client}",
                                severity="critical",
                                affected_items=[mission_id],
                                recommendation="Immediate action required: Hire new pilot or delay mission"
                            ))
                
            # For drone conflicts, suggest alternative drones
            elif "drone" in conflict.conflict_id:
                affected_mission_ids = [item for item in conflict.affected_items if item.startswith('PRJ')]
                for mission_id in affected_mission_ids:
                    mission = next((m for m in missions if m.project_id == mission_id), None)
                    if mission:
                        # Find alternative drones
                        alternatives = self.find_alternatives(mission, pilots, drones)
                        if alternatives:
                            urgent_actions.append(ConflictDetectionResult(
                                conflict_id=f"urgent_reassign_drone_{mission_id}",
                                description=f"URGENT: Alternative drone available for {mission.client}",
                                severity="high",
                                affected_items=[mission_id],
                                recommendation=f"Immediately reassign to drone {alternatives[0].drone.model} with feasibility {alternatives[0].feasibility_score}%"
                            ))
                        else:
                            urgent_actions.append(ConflictDetectionResult(
                                conflict_id=f"urgent_no_drone_{mission_id}",
                                description=f"URGENT: No alternative drone available for {mission.client}",
                                severity="critical",
                                affected_items=[mission_id],
                                recommendation="Immediate action required: Acquire new drone or delay mission"
                            ))
            
        # Check for missions with critical status issues
        for mission in missions:
            # Check if mission has no assigned pilot or drone but needs to start soon
            has_assigned_pilot = any(p.current_assignment == mission.project_id for p in pilots)
            has_assigned_drone = any(d.current_assignment == mission.project_id for d in drones)
                    
            # Only trigger urgency if mission has incomplete assignment and starts soon
            if not has_assigned_pilot or not has_assigned_drone:
                try:
                    start_date = datetime.strptime(mission.start_date, "%Y-%m-%d")
                    days_until_start = (start_date - datetime.now()).days
                                
                    # If mission starts in less than 3 days and has incomplete assignment, it's urgent
                    if 0 <= days_until_start <= 3:
                        missing_resources = []
                        if not has_assigned_pilot:
                            missing_resources.append("pilot")
                        if not has_assigned_drone:
                            missing_resources.append("drone")
                                    
                        urgent_actions.append(ConflictDetectionResult(
                            conflict_id=f"urgent_pending_mission_{mission.project_id}",
                            description=f"URGENT: Mission {mission.client} starts in {days_until_start} days with missing {', '.join(missing_resources)}",
                            severity="high",
                            affected_items=[mission.project_id],
                            recommendation="Immediately assign missing resources to meet deadline"
                        ))
                except ValueError:
                    logger.warning(f"Date parsing failed for mission {mission.project_id}")
            
        return urgent_actions