# Global tracker for staff hours
# Format: { "Staff Name": total_hours }
staff_hours = {}

def update_hours(staff_name, hours):
    if staff_name not in staff_hours:
        staff_hours[staff_name] = 0
    staff_hours[staff_name] += hours

def get_hours(staff_name):
    return staff_hours.get(staff_name, 0)
