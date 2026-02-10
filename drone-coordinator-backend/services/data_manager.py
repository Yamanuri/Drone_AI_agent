"""
Data management service - handles CSV and Google Sheets sync
"""

import pandas as pd
import os
import logging
from typing import List, Optional
from datetime import datetime
from pathlib import Path

from models import PilotData, DroneData, MissionData

logger = logging.getLogger(__name__)

class DataManager:
    """Manages data loading from CSV and Google Sheets."""
    
    def __init__(self):
        """Initialize data manager with CSV paths."""
        self.pilots_csv = os.getenv("PILOTS_CSV_PATH", "data/pilot_roster.csv")
        self.drones_csv = os.getenv("DRONES_CSV_PATH", "data/drone_fleet.csv")
        self.missions_csv = os.getenv("MISSIONS_CSV_PATH", "data/missions.csv")
        
        self._pilots: List[PilotData] = []
        self._drones: List[DroneData] = []
        self._missions: List[MissionData] = []
        
        self.last_sync_time = None
        self.load_from_csv()
    
    # ========================================================================
    # CSV OPERATIONS
    # ========================================================================
    
    def load_from_csv(self) -> bool:
        """Load data from local CSV files."""
        try:
            logger.info("Loading data from CSV files...")
            
            # Load pilots
            if os.path.exists(self.pilots_csv):
                pilots_df = pd.read_csv(self.pilots_csv)
                self._pilots = self._parse_pilots_csv(pilots_df)
                logger.info(f"Loaded {len(self._pilots)} pilots from CSV")
            
            # Load drones
            if os.path.exists(self.drones_csv):
                drones_df = pd.read_csv(self.drones_csv)
                self._drones = self._parse_drones_csv(drones_df)
                logger.info(f"Loaded {len(self._drones)} drones from CSV")
            
            # Load missions
            if os.path.exists(self.missions_csv):
                missions_df = pd.read_csv(self.missions_csv)
                self._missions = self._parse_missions_csv(missions_df)
                logger.info(f"Loaded {len(self._missions)} missions from CSV")
            
            self.last_sync_time = datetime.now().isoformat()
            return True
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return False
    
    def _parse_pilots_csv(self, df: pd.DataFrame) -> List[PilotData]:
        """Parse pilots DataFrame into model objects."""
        pilots = []
        for _, row in df.iterrows():
            try:
                # Handle skills and certifications as comma-separated values
                skills = [s.strip() for s in str(row['skills']).split(',')] if pd.notna(row.get('skills')) else []
                certs = [c.strip() for c in str(row['certifications']).split(',')] if pd.notna(row.get('certifications')) else []
                
                pilot = PilotData(
                    pilot_id=str(row['pilot_id']),
                    name=str(row['name']),
                    skills=skills,
                    certifications=certs,
                    location=str(row['location']),
                    status=str(row.get('status', 'Available')),
                    current_assignment=row.get('current_assignment') if pd.notna(row.get('current_assignment')) else None,
                    available_from=str(row.get('available_from', ''))
                )
                pilots.append(pilot)
            except Exception as e:
                logger.warning(f"Failed to parse pilot row: {e}")
        return pilots
    
    def _parse_drones_csv(self, df: pd.DataFrame) -> List[DroneData]:
        """Parse drones DataFrame into model objects."""
        drones = []
        for _, row in df.iterrows():
            try:
                capabilities = [c.strip() for c in str(row['capabilities']).split(',')] if pd.notna(row.get('capabilities')) else []
                
                drone = DroneData(
                    drone_id=str(row['drone_id']),
                    model=str(row['model']),
                    capabilities=capabilities,
                    status=str(row.get('status', 'Available')),
                    location=str(row['location']),
                    current_assignment=row.get('current_assignment') if pd.notna(row.get('current_assignment')) else None,
                    maintenance_due=str(row.get('maintenance_due', ''))
                )
                drones.append(drone)
            except Exception as e:
                logger.warning(f"Failed to parse drone row: {e}")
        return drones
    
    def _parse_missions_csv(self, df: pd.DataFrame) -> List[MissionData]:
        """Parse missions DataFrame into model objects."""
        missions = []
        for _, row in df.iterrows():
            try:
                skills = [s.strip() for s in str(row['required_skills']).split(',')] if pd.notna(row.get('required_skills')) else []
                certs = [c.strip() for c in str(row['required_certs']).split(',')] if pd.notna(row.get('required_certs')) else []
                
                mission = MissionData(
                    project_id=str(row['project_id']),
                    client=str(row['client']),
                    location=str(row['location']),
                    required_skills=skills,
                    required_certs=certs,
                    start_date=str(row['start_date']),
                    end_date=str(row['end_date']),
                    priority=str(row.get('priority', 'Standard'))
                )
                missions.append(mission)
            except Exception as e:
                logger.warning(f"Failed to parse mission row: {e}")
        return missions
    
    # ========================================================================
    # GETTER METHODS
    # ========================================================================
    
    def get_pilots(self) -> List[PilotData]:
        """Get all pilots."""
        return self._pilots
    
    def get_drones(self) -> List[DroneData]:
        """Get all drones."""
        return self._drones
    
    def get_missions(self) -> List[MissionData]:
        """Get all missions."""
        return self._missions
    
    def get_pilot_by_id(self, pilot_id: str) -> Optional[PilotData]:
        """Get pilot by ID."""
        for pilot in self._pilots:
            if pilot.pilot_id == pilot_id:
                return pilot
        return None
    
    def get_drone_by_id(self, drone_id: str) -> Optional[DroneData]:
        """Get drone by ID."""
        for drone in self._drones:
            if drone.drone_id == drone_id:
                return drone
        return None
    
    def get_mission_by_id(self, mission_id: str) -> Optional[MissionData]:
        """Get mission by ID."""
        for mission in self._missions:
            if mission.project_id == mission_id:
                return mission
        return None
    
    # ========================================================================
    # GOOGLE SHEETS SYNC (TODO - implement with google-api-python-client)
    # ========================================================================
    
    def sync_from_google_sheets(self) -> dict:
        """Sync data from Google Sheets."""
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            # Load credentials
            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "./credentials.json")
            credentials = Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Create Sheets API client
            service = build('sheets', 'v4', credentials=credentials)
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if not sheet_id:
                logger.error("GOOGLE_SHEET_ID not set in environment variables")
                return {"status": "error", "message": "GOOGLE_SHEET_ID not configured"}
            
            # Get sheet names from environment variables
            pilots_sheet_name = os.getenv("PILOTS_SHEET_NAME", "Pilot Roster")
            drones_sheet_name = os.getenv("DRONES_SHEET_NAME", "Drone Fleet")
            missions_sheet_name = os.getenv("MISSIONS_SHEET_NAME", "Missions")
            
            # Read all sheets
            result = service.spreadsheets().values().batchGet(
                spreadsheetId=sheet_id,
                ranges=[
                    f'"{pilots_sheet_name}"!A:H',
                    f'"{drones_sheet_name}"!A:H',
                    f'"{missions_sheet_name}"!A:H'
                ]
            ).execute()
            
            values = result.get('valueRanges', [])
            
            # Parse pilots
            if len(values) > 0 and values[0].get('values'):
                pilots_df = pd.DataFrame(
                    values[0]['values'][1:],  # Skip header
                    columns=values[0]['values'][0]
                )
                self._pilots = self._parse_pilots_csv(pilots_df)
                logger.info(f"Loaded {len(self._pilots)} pilots from Google Sheets")
            
            # Parse drones
            if len(values) > 1 and values[1].get('values'):
                drones_df = pd.DataFrame(
                    values[1]['values'][1:],
                    columns=values[1]['values'][0]
                )
                self._drones = self._parse_drones_csv(drones_df)
                logger.info(f"Loaded {len(self._drones)} drones from Google Sheets")
            
            # Parse missions
            if len(values) > 2 and values[2].get('values'):
                missions_df = pd.DataFrame(
                    values[2]['values'][1:],
                    columns=values[2]['values'][0]
                )
                self._missions = self._parse_missions_csv(missions_df)
                logger.info(f"Loaded {len(self._missions)} missions from Google Sheets")
            
            self.last_sync_time = datetime.now().isoformat()
            logger.info("✅ Successfully synced from Google Sheets")
            return {"status": "success", "synced_from": "google_sheets", "records": {
                "pilots": len(self._pilots),
                "drones": len(self._drones),
                "missions": len(self._missions)
            }}
            
        except FileNotFoundError:
            logger.error("Google Sheets credentials file not found")
            logger.info("Falling back to CSV files")
            self.load_from_csv()
            return {"status": "fallback_to_csv", "error": "Credentials file not found"}
        except Exception as e:
            logger.error(f"Google Sheets sync failed: {e}")
            logger.info("Falling back to CSV files")
            self.load_from_csv()
            return {"status": "fallback_to_csv", "error": str(e)}
    
    def sync_to_google_sheets(self) -> dict:
        """Sync local data back to Google Sheets."""
        try:
            from google.oauth2.service_account import Credentials
            from googleapiclient.discovery import build
            
            # Load credentials
            credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS", "./credentials.json")
            credentials = Credentials.from_service_account_file(
                credentials_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Create Sheets API client
            service = build('sheets', 'v4', credentials=credentials)
            sheet_id = os.getenv("GOOGLE_SHEET_ID")
            
            if not sheet_id:
                logger.error("GOOGLE_SHEET_ID not set in environment variables")
                return {"status": "error", "message": "GOOGLE_SHEET_ID not configured"}
            
            # Get sheet name from environment variable
            pilots_sheet_name = os.getenv("PILOTS_SHEET_NAME", "Pilot Roster")
            
            # Prepare pilot data for upload
            pilot_values = [['pilot_id', 'name', 'skills', 'certifications', 'location', 'status', 'current_assignment', 'available_from']]
            for pilot in self._pilots:
                pilot_values.append([
                    pilot.pilot_id,
                    pilot.name,
                    ', '.join(pilot.skills),
                    ', '.join(pilot.certifications),
                    pilot.location,
                    pilot.status,
                    pilot.current_assignment if pilot.current_assignment else '',
                    pilot.available_from
                ])
            
            # Update Pilot Roster sheet
            range_name = f'"{pilots_sheet_name}"!A:H'
            body = {
                'values': pilot_values
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            logger.info(f"✅ Successfully updated Pilot Roster with {len(self._pilots)} records")
            
            # Also update drones if needed
            drones_sheet_name = os.getenv("DRONES_SHEET_NAME", "Drone Fleet")
            drone_values = [['drone_id', 'model', 'capabilities', 'status', 'location', 'current_assignment', 'maintenance_due', '']]  # Last column empty
            for drone in self._drones:
                drone_values.append([
                    drone.drone_id,
                    drone.model,
                    ', '.join(drone.capabilities),
                    drone.status,
                    drone.location,
                    drone.current_assignment if drone.current_assignment else '',
                    drone.maintenance_due,
                    ''  # Empty last column
                ])
            
            # Update Drone Fleet sheet
            drone_range_name = f'"{drones_sheet_name}"!A:H'
            drone_body = {
                'values': drone_values
            }
            
            drone_result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=drone_range_name,
                valueInputOption='RAW',
                body=drone_body
            ).execute()
            
            logger.info(f"✅ Successfully updated Drone Fleet with {len(self._drones)} records")
            
            # Also update missions if needed
            missions_sheet_name = os.getenv("MISSIONS_SHEET_NAME", "Missions")
            mission_values = [['project_id', 'client', 'location', 'required_skills', 'required_certs', 'start_date', 'end_date', 'priority']]
            for mission in self._missions:
                mission_values.append([
                    mission.project_id,
                    mission.client,
                    mission.location,
                    ', '.join(mission.required_skills),
                    ', '.join(mission.required_certs),
                    mission.start_date,
                    mission.end_date,
                    mission.priority
                ])
            
            # Update Missions sheet
            mission_range_name = f'"{missions_sheet_name}"!A:H'
            mission_body = {
                'values': mission_values
            }
            
            mission_result = service.spreadsheets().values().update(
                spreadsheetId=sheet_id,
                range=mission_range_name,
                valueInputOption='RAW',
                body=mission_body
            ).execute()
            
            logger.info(f"✅ Successfully updated Missions with {len(self._missions)} records")
            
            return {
                "status": "success",
                "synced_to": "google_sheets",
                "updated_records": {
                    "pilots": len(self._pilots),
                    "drones": len(self._drones),
                    "missions": len(self._missions)
                },
                "pilots_updated": result.get('updatedCells', 0),
                "drones_updated": drone_result.get('updatedCells', 0),
                "missions_updated": mission_result.get('updatedCells', 0)
            }
        except FileNotFoundError:
            logger.error("Google Sheets credentials file not found")
            return {"status": "error", "message": "Credentials file not found"}
        except Exception as e:
            logger.error(f"Google Sheets write sync failed: {e}")
            raise
