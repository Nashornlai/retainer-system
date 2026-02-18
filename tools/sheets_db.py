import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import json
import sqlite3
from datetime import datetime

# Scope for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_gspread_client():
    """
    Authenticates with Google Sheets using Streamlit Secrets.
    Expects 'gcp_service_account' in st.secrets.
    """
    try:
        if "gcp_service_account" not in st.secrets:
            # Fallback for local development if secrets.toml is not used but json file exists
            # (Optional, but good for testing)
            return None
            
        # Load from secrets
        service_account_info = st.secrets["gcp_service_account"]
        
        credentials = Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES
        )
        
        client = gspread.authorize(credentials)
        return client
    except Exception as e:
        print(f"❌ Google Sheets Auth Failed: {e}")
        return None

def sync_sqlite_to_sheets(sqlite_db_path="leads.db", sheet_name="Retainer Leads"):
    """
    Reads all leads from SQLite and overwrites the Google Sheet.
    Used as 'Save' mechanism.
    """
    client = get_gspread_client()
    if not client:
        return False, "Auth failed"
        
    try:
        # Open Sheet
        try:
            sheet = client.open(sheet_name).sheet1
        except gspread.SpreadsheetNotFound:
            return False, f"Spreadsheet '{sheet_name}' not found. Please create it and share with bot."

        # Read SQLite
        conn = sqlite3.connect(sqlite_db_path)
        df = pd.read_sql_query("SELECT * FROM leads", conn)
        conn.close()
        
        if df.empty:
            return True, "No data to sync"

        # Convert date columns to string to avoid serialization errors
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str)
                
        # Prepare data for upload
        # fillna with empty string because JSON/Sheets doesn't like NaN
        df_clean = df.fillna("")
        
        # Update Sheet
        # Update Sheet
        # clear() then update() is safest for full sync
        sheet.clear()
        
        # Use explicit range and values to be safe with different gspread versions
        data = [df_clean.columns.values.tolist()] + df_clean.values.tolist()
        try:
            # Newer gspread
            sheet.update(range_name='A1', values=data)
        except TypeError:
            # Older gspread fallback
            sheet.update('A1', data)
        
        return True, f"Synced {len(df)} rows to Sheets"
        
    except Exception as e:
        return False, str(e)

def sync_sheets_to_sqlite(sqlite_db_path="leads.db", sheet_name="Retainer Leads"):
    """
    Reads all data from Google Sheet and restores it to SQLite.
    Used on App Startup to restore persistence.
    """
    client = get_gspread_client()
    if not client:
        return False, "Auth failed"
        
    try:
        # Open Sheet
        try:
            sheet = client.open(sheet_name).sheet1
        except gspread.SpreadsheetNotFound:
            return False, f"Spreadsheet '{sheet_name}' not found."
            
        # Get all records
        data = sheet.get_all_records()
        
        if not data:
            return True, "Sheet is empty, nothing to restore."
            
        df = pd.DataFrame(data)
        
        # Connect to SQLite
        conn = sqlite3.connect(sqlite_db_path)
        
        # Replace 'leads' table with sheet data
        # We use 'replace' to ensure schema matches sheet, 
        # BUT we must ensure the schema is compatible with our app logic.
        # Ideally, we should upsert, but for MVP 'replace' on startup is okay 
        # IF the sheet has all columns.
        
        # Safety: Ensure critical columns exist if sheet is partial? 
        # For now, assume Sheet is the Source of Truth.
        df.to_sql("leads", conn, if_exists="replace", index=False)
        
        conn.close()
        return True, f"Restored {len(df)} rows from Sheets"
        
    except Exception as e:
        return False, str(e)
