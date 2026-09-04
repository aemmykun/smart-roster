# models.py
from sqlalchemy import create_engine, Column, Integer, String, Date, Time
from sqlalchemy.orm import declarative_base, sessionmaker

# connect_args needed for sqlite with multithreaded fastAPI
engine = create_engine("sqlite:///roster.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class Staff(Base):
    __tablename__ = "staff"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(String, index=True)
    name = Column(String)
    role = Column(String)
    email = Column(String)
    availability = Column(String)

class Forecast(Base):
    __tablename__ = "forecast"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(String, index=True)
    date = Column(Date, index=True)
    occupancy = Column(Integer)

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(String, index=True)
    date = Column(Date, index=True)
    staff = Column(String, index=True)
    role = Column(String, index=True)
    shift = Column(String)

class Coverage(Base):
    __tablename__ = "coverage"
    id = Column(Integer, primary_key=True)
    workspace_id = Column(String, index=True)
    date = Column(Date, index=True)
    role = Column(String, index=True)
    demand = Column(Integer)
    assigned = Column(Integer)

Base.metadata.create_all(engine)