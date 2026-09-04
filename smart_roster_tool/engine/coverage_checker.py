def check_coverage(date, demand, assigned):
    """
    Compare demand vs assigned staff to determine coverage status.
    """
    # Count assigned by role
    assigned_counts = {}
    for _, role, _ in assigned:
        assigned_counts[role] = assigned_counts.get(role, 0) + 1
        
    # Validating total coverage instead of individual roles for the summary report

    
    # Better approach for the simple report:
    total_needed = sum(demand.values())
    total_assigned = len(assigned)
    
    return {
        "Date": date,
        "Total Demand": total_needed,
        "Total Assigned": total_assigned,
        "Status": "OK" if total_assigned >= total_needed else "UNDERSTAFFED"
    }
