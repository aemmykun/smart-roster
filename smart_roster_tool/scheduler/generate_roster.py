import pandas as pd
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path so we can import 'engine'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Local modules
from engine.demand_calculator import calculate_demand
from engine.staff_allocator import assign_staff
from engine.coverage_checker import check_coverage
from engine.hour_tracker import staff_hours
# from notify.email_sender import notify_staff, notify_manager_summary
# from notify.push_sender import notify_push
from api.database import save_to_db
from models import engine

# Load environment variables
load_dotenv()

def main():
    if len(sys.argv) < 2:
        print("Error: Workspace ID required")
        sys.exit(1)
        
    workspace_id = sys.argv[1]
    print(f"Generating roster for Workspace: {workspace_id}")

    # --- Load data from DB ---
    # Read forecast (column names must match expected: 'Date Range', 'Occupancy')
    forecast_query = f"SELECT date as 'Date Range', occupancy as 'Occupancy' FROM forecast WHERE workspace_id = '{workspace_id}'"
    forecast = pd.read_sql(forecast_query, engine)
    
    if forecast.empty:
        print("No forecast data found.")
        return

    forecast["Date Range"] = pd.to_datetime(forecast["Date Range"])

    # Read staff (column names must match expected: 'Name', 'Role', 'Availability', etc)
    staff_query = f"SELECT name as 'Name', role as 'Role', availability as 'Availability', email as 'Email' FROM staff WHERE workspace_id = '{workspace_id}'"
    staff_dir = pd.read_sql(staff_query, engine)
    
    # We need to ensure 'Max_Hours' exists if used by logic, defaulting to 40
    staff_dir['Max_Hours'] = 40 

    if staff_dir.empty:
        print("No staff data found.")
        # We might still want to generate empty roster to clear old one?
        # But for now return
        return

    # --- Build roster ---
    roster_output = []
    coverage_output = []

    for _, row in forecast.iterrows():
        date = row["Date Range"]
        demand = calculate_demand(row)
        # Pass staff_dir and current roster_output (for conflict check) to allocator
        assigned = assign_staff(date, demand, staff_dir, roster_output)

        # Save assignments
        for staff, role, shift in assigned:
            roster_output.append({
                "Date": date,
                "Staff": staff,
                "Role": role,
                "Shift": shift
            })

        # Coverage check
        coverage_output.append(check_coverage(date, demand, assigned))

    roster_df = pd.DataFrame(roster_output)
    coverage_df = pd.DataFrame(coverage_output)

    # --- Save to DB for API ---
    save_to_db(roster_df, coverage_df, workspace_id)
    
    # --- Notifications / Export (Skipped for Web Multi-tenant) ---
    # notify_staff(roster_df, staff_dir)
    # notify_manager_summary(roster_df, coverage_df)
    # notify_push(roster_df, staff_dir)

if __name__ == "__main__":
    main()