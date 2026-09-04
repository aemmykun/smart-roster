from models import SessionLocal, Staff, Forecast
from datetime import date, timedelta
import random

def seed_data():
    session = SessionLocal()
    workspace_id = "demo-workspace"
    
    # 1. Clear existing data for this workspace to start fresh
    session.query(Staff).filter(Staff.workspace_id == workspace_id).delete()
    session.query(Forecast).filter(Forecast.workspace_id == workspace_id).delete()
    
    # 2. Add Sample Staff
    sample_staff = [
        {"name": "Alice Johnson", "role": "Housekeeper", "email": "alice@example.com", "availability": "Mon;Tue;Wed;Thu;Fri"},
        {"name": "Bob Smith", "role": "Housekeeper", "email": "bob@example.com", "availability": "Wed;Thu;Fri;Sat;Sun"},
        {"name": "Charlie Brown", "role": "Housekeeper", "email": "charlie@example.com", "availability": "Mon;Tue;Sat;Sun"},
        {"name": "Diana Ross", "role": "Supervisor", "email": "diana@example.com", "availability": "Mon;Tue;Wed;Thu;Fri;Sat;Sun"},
        {"name": "Eve Adams", "role": "Housekeeper", "email": "eve@example.com", "availability": "Mon;Wed;Fri"},
    ]
    
    for s in sample_staff:
        new_staff = Staff(
            workspace_id=workspace_id,
            name=s["name"],
            role=s["role"],
            email=s["email"],
            availability=s["availability"]
        )
        session.add(new_staff)
        
    # 3. Add Sample Forecast for next 7 days
    today = date.today()
    for i in range(7):
        target_date = today + timedelta(days=i)
        new_forecast = Forecast(
            workspace_id=workspace_id,
            date=target_date,
            occupancy=random.randint(20, 50)
        )
        session.add(new_forecast)
        
    session.commit()
    print(f"✅ Seeded data for Workspace: {workspace_id}")
    session.close()

if __name__ == "__main__":
    seed_data()
