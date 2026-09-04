import smtplib
import ssl
import os
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
MANAGER_EMAIL = os.getenv("MANAGER_EMAIL")

def _send_email(to_email, subject, body):
    if not EMAIL_USER or not EMAIL_PASS:
        print(f"⚠️  Skipping email to {to_email} (Credentials not set in .env)")
        return

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print(f"✅ Email sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email to {to_email}: {e}")

def notify_staff(roster_df, staff_dir):
    """
    Send individual roster emails to each staff member.
    """
    print("--- Sending Staff Notifications ---")
    
    # Merge roster with staff details to get emails
    # Assuming staff_dir has 'Name' and 'Email'
    merged = roster_df.merge(staff_dir, left_on='Staff', right_on='Name', how='left')
    
    # Group by staff so we send one email per person with multiple shifts
    for staff_name, group in merged.groupby('Staff'):
        email_address = group['Email'].iloc[0] if 'Email' in group.columns and not pd.isna(group['Email'].iloc[0]) else None
        
        if not email_address:
            print(f"⚠️  No email found for {staff_name}")
            continue

        shifts_text = ""
        for _, row in group.iterrows():
            date_str = row['Date'].strftime('%Y-%m-%d')
            shifts_text += f"- {date_str}: {row['Shift']} ({row['Role']})\n"
            
        subject = f"Your Roster for {group['Date'].min().strftime('%b %d')} - {group['Date'].max().strftime('%b %d')}"
        body = f"Hi {staff_name},\n\nHere are your assigned shifts:\n\n{shifts_text}\nThanks,\nManagement"
        
        _send_email(email_address, subject, body)

import pandas as pd # Needed for isna check inside the function if not available globally

def notify_manager_summary(roster_df, coverage_df):
    """
    Send a summary email to the manager.
    """
    print("--- Sending Manager Summary ---")
    if not MANAGER_EMAIL:
        print("⚠️  No MANAGER_EMAIL set in .env")
        return

    total_shifts = len(roster_df)
    understaffed_days = coverage_df[coverage_df['Status'] == 'UNDERSTAFFED']
    
    status_text = "All days covered."
    if not understaffed_days.empty:
        status_text = f"⚠️ WARNING: {len(understaffed_days)} days are understaffed!"
        
    subject = "Weekly Roster Generation Report"
    body = f"""
    Roster Generation Complete.
    
    Total Shifts Assigned: {total_shifts}
    Coverage Status: {status_text}
    
    Please check the attached report (or dashboard) for full details.
    
    Best,
    Smart Roster Tool
    """
    
    _send_email(MANAGER_EMAIL, subject, body)
