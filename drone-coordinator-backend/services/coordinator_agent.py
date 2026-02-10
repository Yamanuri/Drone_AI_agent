"""
AI Coordinator Agent - OpenAI-powered conversational interface
"""

import logging
import os
from datetime import datetime
from typing import List, Optional

from openai import OpenAI
from models import PilotData, DroneData, MissionData

logger = logging.getLogger(__name__)

class CoordinatorAgent:
    """AI agent for conversational coordination powered by OpenAI."""
    
    def __init__(self):
        """Initialize OpenAI client."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not found - agent will use rule-based responses only")
        
        self.client = OpenAI(api_key=api_key) if api_key else None
        self.model = "gpt-3.5-turbo"
        self.conversation_history = []
    
    def process_query(
        self,
        user_message: str,
        pilots: List[PilotData],
        drones: List[DroneData],
        missions: List[MissionData]
    ) -> str:
        """Process user query and return response."""
        
        # If no OpenAI key, use rule-based response
        if not self.client:
            return self._rule_based_response(user_message, pilots, drones, missions)
        
        try:
            # Prepare context
            context = self._prepare_context(pilots, drones, missions)
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_message
            })
            
            # Create system prompt
            system_prompt = f"""You are a Drone Operations Coordinator AI Agent for Skylark Drones.
You help manage pilot assignments, drone fleet inventory, and mission coordination.

Current Fleet Data:
{context}

Your responsibilities:
1. Answer questions about pilot availability and skills
2. Identify drone capabilities and status
3. Suggest pilot-drone assignments for missions
4. Detect conflicts (double-booking, skill mismatches, location issues)
5. Handle urgent mission reassignments
6. Provide operational status updates

Keep responses concise and actionable. Use available data to make informed recommendations."""
            
            # Get response from OpenAI
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt}
                ] + self.conversation_history,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            return assistant_message
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._rule_based_response(user_message, pilots, drones, missions)
    
    def _prepare_context(
        self, pilots: List[PilotData], drones: List[DroneData], missions: List[MissionData]
    ) -> str:
        """Prepare fleet data context for AI."""
        context_lines = []
        
        # Pilots summary
        context_lines.append("PILOTS:")
        available_pilots = [p for p in pilots if p.status == "Available"]
        context_lines.append(f"  - Total: {len(pilots)}, Available: {len(available_pilots)}")
        for pilot in available_pilots[:5]:  # Show first 5
            skills = ", ".join(pilot.skills) if pilot.skills else "General"
            context_lines.append(f"    • {pilot.name} ({pilot.location}): {skills}")
        
        # Drones summary
        context_lines.append("\nDRONES:")
        available_drones = [d for d in drones if d.status == "Available"]
        context_lines.append(f"  - Total: {len(drones)}, Available: {len(available_drones)}")
        for drone in available_drones[:5]:  # Show first 5
            capabilities = ", ".join(drone.capabilities) if drone.capabilities else "RGB"
            context_lines.append(f"    • {drone.model} ({drone.location}): {capabilities}")
        
        # Missions summary
        context_lines.append("\nMISSIONS:")
        context_lines.append(f"  - Total: {len(missions)}")
        for mission in missions[:5]:  # Show first 5
            context_lines.append(f"    • {mission.client} ({mission.location}): Priority={mission.priority}")
        
        return "\n".join(context_lines)
    
    def _rule_based_response(
        self, user_message: str, pilots: List[PilotData], drones: List[DroneData], missions: List[MissionData]
    ) -> str:
        """Generate rule-based response when OpenAI is unavailable."""
        message_lower = user_message.lower()
        
        # Available pilots
        if "available" in message_lower and "pilot" in message_lower:
            available = [p for p in pilots if p.status == "Available"]
            if not available:
                return "No pilots are currently available."
            return "Available pilots:\n" + "\n".join([
                f"• {p.name} ({p.location}): {', '.join(p.skills) if p.skills else 'General flying'}"
                for p in available
            ])
        
        # Available drones
        if "available" in message_lower and "drone" in message_lower:
            available = [d for d in drones if d.status == "Available"]
            if not available:
                return "No drones are currently available."
            return "Available drones:\n" + "\n".join([
                f"• {d.model} ({d.location}): {', '.join(d.capabilities) if d.capabilities else 'RGB capability'}"
                for d in available
            ])
        
        # Status overview
        if "status" in message_lower:
            available_pilots = len([p for p in pilots if p.status == "Available"])
            available_drones = len([d for d in drones if d.status == "Available"])
            return f"""**Operations Status:**
- Total Pilots: {len(pilots)} (Available: {available_pilots})
- Total Drones: {len(drones)} (Available: {available_drones})
- Total Missions: {len(missions)}

Ready to help with assignments and conflict resolution."""
        
        # Conflicts
        if "conflict" in message_lower:
            pilot_issues = [p for p in pilots if p.status != "Available"]
            drone_issues = [d for d in drones if d.status != "Available"]
            
            issues = []
            if pilot_issues:
                issues.append(f"Unavailable pilots ({len(pilot_issues)}): {', '.join([p.name for p in pilot_issues])}")
            if drone_issues:
                issues.append(f"Unavailable drones ({len(drone_issues)}): {', '.join([d.model for d in drone_issues])}")
            
            if not issues:
                return "No major conflicts detected. All pilots and drones are ready."
            return "**Potential Conflicts Detected:**\n" + "\n".join([f"• {issue}" for issue in issues])
        
        # Default response
        return """I can help with:
- "Show available pilots" - List available pilots
- "Show available drones" - List available drones
- "Status" - Operations overview
- "Check conflicts" - Identify issues
- "Assign [mission]" - Suggest assignment for mission

What would you like to know?"""
    
    def get_timestamp(self) -> str:
        """Get current timestamp."""
        return datetime.now().isoformat()
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history = []
