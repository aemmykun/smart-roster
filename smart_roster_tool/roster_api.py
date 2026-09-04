from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from models import SessionLocal, Assignment, Coverage, Staff, Forecast
from datetime import date, datetime
from pydantic import BaseModel
import pandas as pd
import subprocess
import sys
import os

app = FastAPI()

# Enable CORS for the UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (css, js, etc.)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def read_index():
    return FileResponse('index.html')

@app.get("/style.css")
async def read_css():
    return FileResponse('style.css')

class StaffModel(BaseModel):
    name: str
    role: str
    email: str
    availability: str
    workspace_id: str

class ForecastModel(BaseModel):
    date: str
    occupancy: int
    workspace_id: str

class GenerateModel(BaseModel):
    workspace_id: str

@app.post("/staff")
def add_staff(staff: StaffModel):
    session = SessionLocal()
    try:
        new_staff = Staff(
            workspace_id=staff.workspace_id,
            name=staff.name,
            role=staff.role,
            email=staff.email,
            availability=staff.availability
        )
        session.add(new_staff)
        session.commit()
        return {"status": "success", "message": f"Added {staff.name}"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.post("/forecast")
def update_forecast(data: ForecastModel):
    session = SessionLocal()
    try:
        f_date = datetime.strptime(data.date, "%Y-%m-%d").date()
        # Check if exists
        existing = session.query(Forecast).filter(
            Forecast.workspace_id == data.workspace_id,
            Forecast.date == f_date
        ).first()

        if existing:
            existing.occupancy = data.occupancy
        else:
            new_forecast = Forecast(
                workspace_id=data.workspace_id,
                date=f_date,
                occupancy=data.occupancy
            )
            session.add(new_forecast)
        
        session.commit()
        return {"status": "success", "message": f"Updated forecast for {data.date}"}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        session.close()

@app.post("/generate")
def trigger_generation(data: GenerateModel):
    """Trigger the python script to generate roster for a specific workspace"""
    try:
        # Run the generate_roster.py script with workspace_id as argument
        subprocess.run([sys.executable, "scheduler/generate_roster.py", data.workspace_id], check=True)
        return {"status": "success", "message": "Roster generated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/roster/{yyyy_mm_dd}")
def get_roster(yyyy_mm_dd: str, workspace_id: str = Query(...)):
    y, m, d = map(int, yyyy_mm_dd.split("-"))
    session = SessionLocal()
    data = session.query(Assignment).filter(
        Assignment.workspace_id == workspace_id,
        Assignment.date == date(y, m, d)
    ).all()
    session.close()
    return [{"staff": a.staff, "role": a.role, "shift": a.shift} for a in data]

@app.get("/coverage/{yyyy_mm_dd}")
def get_coverage(yyyy_mm_dd: str, workspace_id: str = Query(...)):
    y, m, d = map(int, yyyy_mm_dd.split("-"))
    session = SessionLocal()
    cov = session.query(Coverage).filter(
        Coverage.workspace_id == workspace_id,
        Coverage.date == date(y, m, d)
    ).all()
    session.close()
    return [{"role": c.role, "demand": c.demand, "assigned": c.assigned} for c in cov]
