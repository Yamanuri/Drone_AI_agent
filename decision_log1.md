# Decision Log - Drone Operations Coordinator

## Key Assumptions I Made

### 1. Google Sheets Integration Scope
When the requirements mentioned reading from "both sheets," I interpreted this to mean the Pilot Roster and Drone Fleet sheets, plus I included the Missions sheet as well since all three are needed for complete system functionality. I assumed the Google Sheets API would be accessed through service account authentication, and that the data structure in Google Sheets would match the CSV format we're using as a fallback.

### 2. Urgent Reassignments Interpretation
I interpreted "urgent reassignments" as the system's ability to identify critical conflicts requiring immediate action and automatically suggest alternative assignments. I assumed that urgent situations would include pilot/dronedouble-booking, upcoming missions with incomplete assignments, and resource conflicts that could disrupt operations.

### 3. Data Consistency Model
I assumed that Google Sheets should serve as the primary source of truth with CSV files as backup. I also assumed that write operations to Google Sheets would be batched to minimize API usage, and that conflicts between local and remote data should favor the Google Sheets data as the authoritative source.

### 4. Conflict Detection Logic
I assumed that date overlaps between missions constitute double-booking conflicts. I also assumed that "Available" status means a resource is ready for assignment, and that skill/certification matching should be case-insensitive for user convenience and flexibility.

## Trade-offs I Chose and Why

### 1. Technology Stack Selection
**Trade-off**: Using OpenAI API vs. rule-based responses
**Why I chose this**: OpenAI provides a more natural conversational experience, but it costs money and depends on an external service. I implemented a rule-based fallback for offline functionality so the system still works when the API is unavailable.

### 2. Data Storage Approach
**Trade-off**: Google Sheets as primary storage vs. dedicated database
**Why I chose this**: Google Sheets provides easy access for non-technical stakeholders who might need to update rosters, but it has rate limits and slower performance than a dedicated database. I chose it because it makes it easy for team members to collaborate and update data without needing technical access.

### 3. Conflict Resolution Strategy
**Trade-off**: Automatic reassignment vs. manual confirmation
**Why I chose this**: Automatic reassignment could lead to unwanted changes that might disrupt operations. I implemented a suggestion system that requires human confirmation while still highlighting urgent cases that need attention.

### 4. Error Handling Philosophy
**Trade-off**: Fail-fast vs. graceful degradation
**Why I chose this**: I chose graceful degradation to maintain system availability. If Google Sheets is unavailable, the system continues to work with CSV data and syncs when connectivity is restored, ensuring operations aren't disrupted.

### 5. Sync Frequency
**Trade-off**: Continuous polling vs. on-demand sync
**Why I chose this**: Continuous polling would hit API limits and consume resources unnecessarily. I chose on-demand sync triggered by user action or specific events, which is more efficient and cost-effective.

## What I Would Do Differently with More Time

### 1. Enhanced Conflict Detection
With more time, I would implement more sophisticated scheduling algorithms that consider travel time between locations, predictive conflict detection based on historical patterns, and advanced optimization algorithms beyond simple feasibility scoring.

### 2. Improved User Experience
I would add real-time notifications for conflicts and urgent situations, a visual timeline view of pilot/dronescalendar, and a mobile-friendly interface for field operations.

### 3. Better Scalability
I would implement a database backend instead of Google Sheets for larger fleets, asynchronous processing for bulk operations, and a caching layer to reduce API calls and improve performance.

### 4. Enhanced Monitoring
I would add detailed analytics on assignment patterns and conflict frequency, a performance metrics dashboard, and automated reporting features.

### 5. Advanced Features
I would add machine learning to predict optimal assignments based on historical success, weather integration for flight safety, and maintenance scheduling automation.

## How I Interpreted "Urgent Reassignments"

### My Definition
I interpreted urgent reassignments as the system's capability to:
1. Automatically detect critical situations requiring immediate action
2. Identify alternative resources when conflicts arise
3. Prioritize recommendations based on urgency level
4. Provide actionable next steps for coordinators

### Implementation Details
- **Critical Situation Detection**: The system monitors for double-bookings, upcoming missions with incomplete assignments, and resource conflicts
- **Alternative Suggestions**: When conflicts are detected, the system automatically searches for alternative pilots/drones with high feasibility scores
- **Priority Ranking**: Urgent situations are flagged with high severity and appear prominently in conflict reports
- **Actionable Recommendations**: Each urgent situation comes with specific suggestions like "Reassign pilot John Doe to mission PRJ001 with feasibility 85%"

### Trigger Conditions
- Pilot assigned to overlapping missions based on date ranges
- Drone assigned to overlapping missions
- Mission starting within 3 days without complete pilot/dronessignment
- Critical conflicts identified during routine conflict detection

This interpretation ensures that the system actively helps coordinators manage unexpected changes rather than just identifying problems. The system becomes proactive in suggesting solutions rather than just pointing out issues.

## Google Sheets 2-Way Sync Implementation

### Technical Architecture
I implemented batchGet operations to read from Pilot Roster, Drone Fleet, and Missions sheets, and update operations to write pilot status and other data back to sheets. I included comprehensive fallback to CSV files when Google Sheets is unavailable, and used service account authentication with the credentials.json file.

### Data Mapping
I mapped the Pilot Roster to the PilotData model with fields like pilot_id, name, skills, certifications, location, status, current_assignment, and available_from. Similarly for Drone Fleet to DroneData and Missions to MissionData models.

### Sync Process
The system reads all three sheets and populates internal data structures when syncing from Sheets, and writes updated data back to corresponding sheets when syncing to Sheets, while preserving data integrity. The system prioritizes Google Sheets as the source of truth when discrepancies occur.

## Conflict Detection Algorithm

### Individual Checks
I implemented skill matching with case-insensitive comparison, certification validation to verify required certifications are held, location verification to confirm pilot/drone is in required location, availability assessment with date range checking for schedule conflicts, capability matching to ensure drone has required capabilities for mission, and status validation to check current status is compatible with assignment.

### Feasibility Scoring
I implemented severity penalties with Low (0%), Medium (15%), and High (40%) penalties. There's also a critical issue multiplier that adds an additional 20% penalty per critical issue. Assignments below 50% feasibility are not recommended.

### Urgent Reassignment Logic
The system detects conflicts requiring immediate attention, automatically finds suitable replacements, ranks alternatives by feasibility score, and provides actionable suggestions with confidence levels.