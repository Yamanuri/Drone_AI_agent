# Decision Log - Drone Operations Coordinator

## Key Assumptions

### 1. Google Sheets Integration Scope
- Assumed that "reading from both sheets" meant reading from Pilot Roster, Drone Fleet, and Missions sheets, as all three are needed for complete system functionality
- Assumed that the Google Sheets API would be accessed through service account authentication
- Assumed that data structure in Google Sheets would match the CSV format used as fallback

### 2. Urgent Reassignments Interpretation
- Interpreted "urgent reassignments" as the system's ability to identify critical conflicts requiring immediate action and automatically suggest alternative assignments
- Assumed that urgent situations include: pilot/dronedouble-booking, upcoming missions with incomplete assignments, and resource conflicts

### 3. Data Consistency Model
- Assumed that Google Sheets serves as the primary source of truth with CSV files as backup
- Assumed that write operations to Google Sheets would be batched to minimize API usage
- Assumed that conflicts between local and remote data would favor the Google Sheets data

### 4. Conflict Detection Logic
- Assumed that date overlaps between missions constitute double-booking conflicts
- Assumed that "Available" status means a resource is ready for assignment
- Assumed that skill/certification matching is case-insensitive for flexibility

## Trade-offs Chosen and Why

### 1. Technology Stack Selection
**Trade-off**: Using OpenAI API vs. rule-based responses
**Reason**: OpenAI provides more natural conversational experience but costs money and depends on external service. Implemented rule-based fallback for offline functionality.

### 2. Data Storage Approach
**Trade-off**: Google Sheets as primary storage vs. dedicated database
**Reason**: Google Sheets provides easy access for non-technical stakeholders but has rate limits and slower performance. Chose it for simplicity of sharing with team members.

### 3. Conflict Resolution Strategy
**Trade-off**: Automatic reassignment vs. manual confirmation
**Reason**: Automatic reassignment could lead to unwanted changes, so implemented suggestion system that requires human confirmation while highlighting urgent cases.

### 4. Error Handling Philosophy
**Trade-off**: Fail-fast vs. graceful degradation
**Reason**: Chose graceful degradation to maintain system availability - if Google Sheets is unavailable, system continues to work with CSV data and syncs when connectivity is restored.

### 5. Sync Frequency
**Trade-off**: Continuous polling vs. on-demand sync
**Reason**: Continuous polling would hit API limits and consume resources unnecessarily. Chose on-demand sync triggered by user action or specific events.

## What Would Be Done Differently with More Time

### 1. Enhanced Conflict Detection
With more time, I would implement:
- More sophisticated scheduling algorithms considering travel time between locations
- Predictive conflict detection based on historical patterns
- Advanced optimization algorithms beyond simple feasibility scoring

### 2. Improved User Experience
- Real-time notifications for conflicts and urgent situations
- Visual timeline view of pilot/dronescalendar
- Mobile-friendly interface for field operations

### 3. Better Scalability
- Database backend instead of Google Sheets for larger fleets
- Asynchronous processing for bulk operations
- Caching layer to reduce API calls and improve performance

### 4. Enhanced Monitoring
- Detailed analytics on assignment patterns and conflict frequency
- Performance metrics dashboard
- Automated reporting features

### 5. Advanced Features
- Machine learning to predict optimal assignments based on historical success
- Weather integration for flight safety
- Maintenance scheduling automation

## How Urgent Reassignments Were Interpreted

### Definition
Urgent reassignments were interpreted as the system's capability to:
1. Automatically detect critical situations requiring immediate action
2. Identify alternative resources when conflicts arise
3. Prioritize recommendations based on urgency level
4. Provide actionable next steps for coordinators

### Implementation Details
- **Critical Situation Detection**: System monitors for double-bookings, upcoming missions with incomplete assignments, and resource conflicts
- **Alternative Suggestions**: When conflicts are detected, the system automatically searches for alternative pilots/drones with high feasibility scores
- **Priority Ranking**: Urgent situations are flagged with high severity and appear prominently in conflict reports
- **Actionable Recommendations**: Each urgent situation comes with specific suggestions like "Reassign pilot John Doe to mission PRJ001 with feasibility 85%"

### Trigger Conditions
- Pilot assigned to overlapping missions based on date ranges
- Drone assigned to overlapping missions
- Mission starting within 3 days without complete pilot/dronessignment
- Critical conflicts identified during routine conflict detection

This interpretation ensures that the system actively helps coordinators manage unexpected changes rather than just identifying problems.