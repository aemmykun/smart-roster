def calculate_demand(forecast_row):
    """
    Calculate staff demand based on forecast data.
    Standard rule: 
    - 1 Room Attendant per 15 rooms (Occupancy).
    - 1 Supervisor if Occupancy > 50.
    """
    occupancy = forecast_row['Occupancy']
    
    housekeepers_needed = max(1, round(occupancy / 15))
    supervisors_needed = 1 if occupancy > 50 else 0
    
    return {
        "Housekeeper": housekeepers_needed,
        "Supervisor": supervisors_needed
    }
