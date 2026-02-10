# Google Sheets Integration Setup Guide

## What Is This?

This guide shows how to set up **2-way sync between the Drone Coordinator and Google Sheets**, so:
- 📥 **Read pilot/drone/mission data** from a shared Google Sheet
- 📤 **Write updates back** to Google Sheets (status changes, assignments)
- 🔄 **Automatic sync** on app startup (can add scheduled syncs)

---

## Architecture

```
Google Sheets (Cloud Source of Truth)
        ↑
        │ sync_from_google_sheets()
        │
        ├─→ [Pilots Tab]
        ├─→ [Drones Tab]
        └─→ [Missions Tab]
        ↑
        │ sync_to_google_sheets()
        │
┌───────┴─────────────────┐
│   FastAPI Backend       │
│  (CSV fallback cache)   │
└─────────────────────────┘
```

---

## Prerequisites

1. **Google Account** (free or workspace)
2. **Google Sheets** with pilot/drone/mission data
3. **Service Account** (Google Cloud credentials)

---

## STEP 1: Create a Google Sheet

1. Open [Google Sheets](https://sheets.google.com)
2. Create new spreadsheet: **"Skylark Drones Fleet Management"**
3. Create 3 sheets (tabs at bottom):
   - **Pilot Roster**
   - **Drone Fleet**
   - **Missions**

### Pilot Roster Sheet

| Column | Format | Example |
|--------|--------|---------|
| A: pilot_id | Text | P001 |
| B: name | Text | Arjun |
| C: skills | Text (comma-separated) | Mapping, Survey |
| D: certifications | Text (comma-separated) | DGCA, Night Ops |
| E: location | Text | Bangalore |
| F: status | Text | Available |
| G: current_assignment | Text | [ProjectID or blank] |
| H: available_from | Date (YYYY-MM-DD) | 2026-02-05 |

**Pilot Roster Tab Headers:**
```
pilot_id | name   | skills            | certifications   | location  | status | current_assignment | available_from
P001     | Arjun  | Mapping, Survey   | DGCA, Night Ops  | Bangalore | Available |              | 2026-02-05
P002     | Neha   | Inspection        | DGCA             | Mumbai    | Assigned | Project-A    | 2026-02-12
P003     | Rohit  | Inspection, Mapping | DGCA           | Mumbai    | Available |              | 2026-02-05
P004     | Sneha  | Survey, Thermal   | DGCA, Night Ops  | Bangalore | On Leave |              | 2026-02-15
```

### Drone Fleet Sheet

| Column | Format | Example |
|--------|--------|---------|
| A: drone_id | Text | D001 |
| B: model | Text | DJI M300 |
| C: capabilities | Text (comma-separated) | LiDAR, RGB |
| D: status | Text | Available |
| E: location | Text | Bangalore |
| F: current_assignment | Text | [ProjectID or blank] |
| G: maintenance_due | Date (YYYY-MM-DD) | 2026-03-01 |

### Missions Sheet

| Column | Format | Example |
|--------|--------|---------|
| A: project_id | Text | PRJ001 |
| B: client | Text | Client A |
| C: location | Text | Bangalore |
| D: required_skills | Text (comma-separated) | Mapping |
| E: required_certs | Text (comma-separated) | DGCA |
| F: start_date | Date (YYYY-MM-DD) | 2026-02-06 |
| G: end_date | Date (YYYY-MM-DD) | 2026-02-08 |
| H: priority | Text | High |

---

## STEP 2: Get Your Google Sheet ID

In the Google Sheets URL:
```
https://docs.google.com/spreadsheets/d/ABC123XYZ789/edit#gid=0
                                      ^^^^^^^^^^^^^^^^
                             This is your SHEET_ID
```

Copy the ID and save it.

---

## STEP 3: Create Service Account

### 3.1 Go to Google Cloud Console
1. Open [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project:
   - Click project dropdown (top left)
   - Click **"NEW PROJECT"**
   - Name: "Drone Coordinator"
   - Create

### 3.2 Enable Google Sheets API
1. In Google Cloud Console, search for **"Google Sheets API"**
2. Click **"ENABLE"**
3. Do the same for **"Google Drive API"**

### 3.3 Create Service Account
1. In Google Cloud Console sidebar, go to **"Service Accounts"**
2. Click **"CREATE SERVICE ACCOUNT"**
   - Service account name: "drone-coordinator"
   - Click **"CREATE AND CONTINUE"**
3. Skip optional steps (click Continue)
4. Click **"CREATE KEY"**
   - Type: **JSON**
   - Click **"CREATE"**
5. A file downloads: **drone-coordinator-xxx.json**
6. Save this file as `credentials.json` in your project root:
   ```
   drone-coordinator-backend/credentials.json
   ```

---

## STEP 4: Share Sheet with Service Account

1. Open **credentials.json** file (text editor)
2. Find the `client_email` field (looks like `xxx@xxx.iam.gserviceaccount.com`)
3. Go back to your Google Sheet
4. Click **"Share"** (top right)
5. Paste the client email
6. Give **"Editor"** permissions
7. Click **"Share"**

---

## STEP 5: Update Configuration

Edit `.env` file:

```dotenv
# Google Sheets Configuration
GOOGLE_SHEETS_CREDENTIALS=./credentials.json
GOOGLE_SHEET_ID=your-sheet-id-here

# Sheet tab names (must match exactly!)
PILOTS_SHEET_NAME=Pilot Roster
DRONES_SHEET_NAME=Drone Fleet
MISSIONS_SHEET_NAME=Missions
```

Replace:
- `your-sheet-id-here` → Your actual sheet ID from Step 2
- Sheet names → Match your actual tab names exactly

---

## STEP 6: Implement Google Sheets Sync

Edit `services/data_manager.py` - replace the TODO sections:

```python
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
        
        # Read all sheets
        result = service.spreadsheets().values().batchGet(
            spreadsheetId=sheet_id,
            ranges=[
                self._get_sheet_range('Pilot Roster'),
                self._get_sheet_range('Drone Fleet'),
                self._get_sheet_range('Missions')
            ]
        ).execute()
        
        values = result.get('valueRanges', [])
        
        # Parse pilots
        if values[0].get('values'):
            pilots_df = pd.DataFrame(
                values[0]['values'][1:],  # Skip header
                columns=values[0]['values'][0]
            )
            self._pilots = self._parse_pilots_csv(pilots_df)
        
        # Parse drones
        if values[1].get('values'):
            drones_df = pd.DataFrame(
                values[1]['values'][1:],
                columns=values[1]['values'][0]
            )
            self._drones = self._parse_drones_csv(drones_df)
        
        # Parse missions
        if values[2].get('values'):
            missions_df = pd.DataFrame(
                values[2]['values'][1:],
                columns=values[2]['values'][0]
            )
            self._missions = self._parse_missions_csv(missions_df)
        
        self.last_sync_time = datetime.now().isoformat()
        logger.info("✅ Successfully synced from Google Sheets")
        return {"status": "success", "synced_from": "google_sheets"}
        
    except Exception as e:
        logger.error(f"Google Sheets sync failed: {e}")
        logger.info("Falling back to CSV files")
        self.load_from_csv()
        return {"status": "fallback_to_csv", "error": str(e)}

def _get_sheet_range(self, sheet_name: str) -> str:
    """Get A1 range notation for sheet."""
    return f"'{sheet_name}'!A:H"  # Adjust 'H' to match your columns
```

---

## STEP 7: Test Sync

1. Start your app normally:
   ```bash
   python main.py  # Terminal 1
   streamlit run app.py  # Terminal 2
   ```

2. In Streamlit, click **"Sync from Google Sheets"** button
   - Should say: ✅ "Data synced from Google Sheets"

3. Check pilot data appears in the Pilots tab

4. Edit a cell in Google Sheets (change a pilot status)

5. Click **"Refresh Data"** in Streamlit

6. Verify the change appears

---

## API Endpoints for Sync

### Manually sync FROM Google Sheets
```bash
curl -X POST http://127.0.0.1:8000/sync/google-sheets
```

Response:
```json
{
  "status": "success",
  "message": "Data synced from Google Sheets"
}
```

### Manually sync TO Google Sheets
```bash
curl -X POST http://127.0.0.1:8000/sync/to-google-sheets
```

---

## Troubleshooting

### ❌ "FileNotFoundError: credentials.json"
**Fix:** 
1. Save service account JSON as `credentials.json` in project root
2. Update `.env`: `GOOGLE_SHEETS_CREDENTIALS=./credentials.json`

### ❌ "Invalid Sheet ID"
**Fix:**
1. Get correct ID from Sheet URL
2. Update `.env`: `GOOGLE_SHEET_ID=your-actual-id`

### ❌ "Permission denied" or 403 error
**Fix:**
1. Share Google Sheet with service account email
2. Give **"Editor"** permissions (not "Viewer")
3. Restart app

### ❌ "Unable to parse columns"
**Fix:**
1. Verify sheet tab names match `.env` exactly (case-sensitive)
2. Verify column headers match expected names
3. Check for extra spaces in column names

### ❌ CSV fallback in logs (sync failed silently)
**Fix:**
1. Check credentials.json exists and is valid JSON
2. Verify APIs enabled in Google Cloud Console:
   - Google Sheets API
   - Google Drive API
3. Check service account has Editor access to sheet

---

## Best Practices

### 1. **Regular Backups**
Keep CSV files as backup:
```bash
cp data/pilot_roster.csv data/pilot_roster.backup.csv
```

### 2. **Avoid Concurrent Edits**
- API syncs on app startup
- Don't edit Google Sheet while API is running
- Queue sync requests if needed

### 3. **Data Format Consistency**
- Use **YYYY-MM-DD** for all dates
- **Comma-separated values** for lists (Mapping, Survey)
- **Consistent column names** (no extra spaces)

### 4. **Monitor Syncs**
- Check logs for sync errors
- API logs to stdout automatically
- Streamlit shows sync success/failure in UI

---

## Advanced: Scheduled Sync

To auto-sync every 5 minutes, add to `main.py`:

```python
from fastapi import BackgroundTasks
import asyncio

# Add this to FastAPI initialization
async def background_sync():
    """Background task to sync every 5 minutes."""
    while True:
        try:
            data_manager.sync_from_google_sheets()
        except Exception as e:
            logger.error(f"Background sync failed: {e}")
        
        await asyncio.sleep(300)  # 5 minutes

# Add to app startup
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(background_sync())
```

---

## Data Flow Diagram

```
Google Sheets                    Your App
     ↓                            ↓
[Pilot Roster Tab]  ←────────→  Pilots Table
[Drone Fleet Tab]   ←────────→  Drones Table
[Missions Tab]      ←────────→  Missions Table
     ↓                            ↓
(Auto-updated)            (CSV fallback cache)
```

---

## FAQ

**Q: Can multiple people edit Google Sheet while app is syncing?**
A: Yes, but wait 30 seconds after edits before syncing to avoid conflicts.

**Q: What happens if Google Sheets is down?**
A: App falls back to CSV files automatically. No data loss.

**Q: Can I write-protect sheets from app?**
A: Yes - give service account "Editor" on specific sheets only.

**Q: How often should I sync?**
A: Every ~5 minutes is good for most use cases. Can adjust in code.

**Q: Do I need Google Workspace?**
A: No, free personal Google accounts work fine.

---

## Support

If you get stuck:
1. Check `.env` file for typos
2. Verify credentials.json is valid (open with text editor)
3. Check Google Cloud Console for API enable status
4. Look at app logs (Terminal 1) for error messages
5. Verify service account has sheet access (check Share button)

---

**Last Updated:** February 10, 2026
