import pandas as pd
from engine.hour_tracker import update_hours, get_hours

def assign_staff(date, demand, staff_dir, previous_assignments):
    """
    Assign staff to meet demand, checking availability and conflicts.
    """
    assigned = []
    
    # Simple day of week string (e.g., "Mon", "Tue")
    day_of_week = date.strftime("%a")
    
    for role, count in demand.items():
        needed = count
        
        # Filter staff by role
        candidates = staff_dir[staff_dir['Role'] == role]
        
        for _, staff in candidates.iterrows():
            if needed <= 0:
                break
            
            name = staff['Name']
            availability = staff['Availability']
            max_hours = staff['Max_Hours']
            current_hours = get_hours(name)
            
            # Check 1: Is staff available this day?
            if day_of_week not in availability:
                continue
                
            # Check 2: Max hours limit (assuming 8 hour shift)
            if current_hours + 8 > max_hours:
                continue
            
            # Check 3: Already assigned today? (Conflict detection)
            # In a real app, you'd check previous_assignments for this specific date
            already_working = False
            for entry in previous_assignments:
                if entry['Date'] == date and entry['Staff'] == name:
                    already_working = True
                    break
            if already_working:
                continue

            # Assign
            # Shift time is hardcoded for now
            shift = "08:00 - 16:00"
            assigned.append((name, role, shift))
            update_hours(name, 8)
            needed -= 1
            
    return assigned
