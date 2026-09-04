from models import SessionLocal, Assignment, Coverage
from datetime import date

def save_to_db(roster_df, coverage_df, workspace_id):
    session = SessionLocal()
    try:
        # Convert 'Date' columns to python date objects if they are pandas timestamps
        # (SQLAlchemy often handles this, but explicit is safer)
        
        # 0. Clean up existing assignments for this workspace/date range to avoid duplicates
        # (Simplified: just delete overlapping dates in this generation)
        dates = []
        if not roster_df.empty:
             dates = roster_df['Date'].dt.date.unique().tolist()
        
        if len(dates) > 0:
             session.query(Assignment).filter(
                 Assignment.workspace_id == workspace_id,
                 Assignment.date.in_(dates)
             ).delete(synchronize_session=False)
             session.query(Coverage).filter(
                 Coverage.workspace_id == workspace_id,
                 Coverage.date.in_(dates)
             ).delete(synchronize_session=False)

        # 1. Save Roster Assignments
        assignments_objects = []
        for _, row in roster_df.iterrows():
            assign = Assignment(
                workspace_id=workspace_id,
                date=row['Date'].date(), # Assumes pandas timestamp
                staff=row['Staff'],
                role=row['Role'],
                shift=row['Shift']
            )
            assignments_objects.append(assign)
        session.add_all(assignments_objects)

        # 2. Save Coverage Stats
        coverage_objects = []
        for _, row in coverage_df.iterrows():
            # Note: Current simple calculator aggregates everything. 
            # We will store it as role='All' for now.
            cov = Coverage(
                workspace_id=workspace_id,
                date=row['Date'].date(),
                role="All", 
                demand=row['Total Demand'],
                assigned=row['Total Assigned']
            )
            coverage_objects.append(cov)
        session.add_all(coverage_objects)

        session.commit()
        print(f"✅ Saved {len(assignments_objects)} assignments and {len(coverage_objects)} coverage records to Database.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error saving to DB: {e}")
    finally:
        session.close()
