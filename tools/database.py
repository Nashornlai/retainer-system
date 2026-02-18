import sqlite3
import hashlib
import os
import pandas as pd
from datetime import datetime

DB_FILE = "leads.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    
    # Users Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Searches Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS searches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            keyword TEXT,
            country TEXT,
            num_leads INTEGER,
            category TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Leads Table
    c.execute('''
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            search_id INTEGER,
            company TEXT,
            website TEXT,
            email TEXT,
            ad_url TEXT,
            ad_image TEXT,
            newsletter_signup BOOLEAN DEFAULT 0,
            cart_abandoned BOOLEAN DEFAULT 0,
            email_sent BOOLEAN DEFAULT 0,
            response_received BOOLEAN DEFAULT 0,
            converted BOOLEAN DEFAULT 0,
            notes TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(search_id) REFERENCES searches(id)
        )
    ''')
    
    # Default Admin User (admin / admin123)
    # Simple SHA256 for prototype
    admin_pw = hashlib.sha256("admin123".encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", admin_pw))
        print("✅ Default admin user created.")
    except sqlite3.IntegrityError:
        pass # Admin already exists
        
    conn.commit()
    conn.close()
    
    # Run Migrations (for existing DBs)
    migrate_db()

def migrate_db():
    """Adds new columns to existing databases without breaking them."""
    conn = get_connection()
    c = conn.cursor()
    
    try:
        c.execute("ALTER TABLE leads ADD COLUMN newsletter_signup BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE leads ADD COLUMN cart_abandoned BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE leads ADD COLUMN email_sent BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE leads ADD COLUMN response_received BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE leads ADD COLUMN converted BOOLEAN DEFAULT 0")
        c.execute("ALTER TABLE leads ADD COLUMN notes TEXT")
        print("✅ Database migrated: Added lead tracking columns.")
    except sqlite3.OperationalError:
        pass # Columns likely already exist

    try:
        c.execute("ALTER TABLE searches ADD COLUMN category TEXT")
        print("✅ Database migrated: Added search category.")
    except sqlite3.OperationalError:
        pass # Column likely already exists
        
    conn.commit()
    conn.close()

def verify_user(username, password):
    conn = get_connection()
    c = conn.cursor()
    pw_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT id, username FROM users WHERE username = ? AND password_hash = ?", (username, pw_hash))
    user = c.fetchone()
    conn.close()
    return user

def save_search_results(user_id, keyword, country, df):
    if df.empty:
        return
        
    conn = get_connection()
    c = conn.cursor()
    
    # 1. Log Search
    c.execute("INSERT INTO searches (user_id, keyword, country, num_leads) VALUES (?, ?, ?, ?)", 
              (user_id, keyword, country, len(df)))
    search_id = c.lastrowid
    
    # 2. Save Leads
    for _, row in df.iterrows():
        c.execute('''
            INSERT INTO leads (user_id, search_id, company, website, email, ad_url, ad_image)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id, 
            search_id, 
            row.get("Company"), 
            row.get("Website"), 
            row.get("Email"), 
            row.get("Ad URL"), 
            row.get("Ad Image")
        ))
        
    conn.commit()
    conn.close()
    return search_id

def get_user_leads(user_id, filter_status='active'):
    """
    filter_status: 'active' (default), 'deleted', 'all'
    """
    conn = get_connection()
    query = '''
        SELECT 
            l.id as ID,
            l.company as Company, 
            l.website as Website, 
            l.email as Email, 
            l.ad_url as 'Ad URL',
            l.ad_image as 'Ad Image',
            l.newsletter_signup as 'Newsletter',
            l.cart_abandoned as 'Warenkorb',
            l.email_sent as 'Angeschrieben',
            l.response_received as 'Antwort',
            l.converted as 'Kunde',
            l.notes as 'Notizen',
            l.deleted as 'Trash',
            l.deletion_reason as 'Grund',
            l.follow_up_date as 'Wiedervorlage',
            l.follow_up_reason as 'Aufgabe',
            l.follow_up_status as 'Status',
            s.keyword as Keyword,
            s.category as Category,
            l.timestamp as Date
        FROM leads l
        JOIN searches s ON l.search_id = s.id
        WHERE l.user_id = ?
    '''
    
    if filter_status == 'active':
        query += " AND (l.deleted = 0 OR l.deleted IS NULL)"
    elif filter_status == 'deleted':
        query += " AND l.deleted = 1"
        
    query += " ORDER BY l.timestamp DESC"
    
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def update_lead(lead_id, column, value):
    conn = get_connection()
    c = conn.cursor()
    
    # Ensure ID is native int (crucial for SQLite matching)
    lead_id = int(lead_id)
    
    try:
        if column == 'Trash':
            # Map 'Trash' UI column to 'deleted' DB column
            # Ensure proper boolean/int casting
            val = 1 if value else 0
            c.execute("UPDATE leads SET deleted = ? WHERE id = ?", (val, lead_id))
        elif column == 'Grund':
            c.execute("UPDATE leads SET deletion_reason = ? WHERE id = ?", (value, lead_id))
        else:
            # Map friendly names to DB columns
            db_col = {
                "Newsletter": "newsletter_signup",
                "Warenkorb": "cart_abandoned",
                "Angeschrieben": "email_sent",
                "Antwort": "response_received",
                "Kunde": "converted",
                "Notizen": "notes"
            }.get(column, column) # Default to original if no mapping
            
            # Handle booleans for generic columns
            if isinstance(value, bool):
                value = 1 if value else 0
                
            query = f"UPDATE leads SET {db_col} = ? WHERE id = ?"
            c.execute(query, (value, lead_id))
            
            # --- Follow-up Logic (Side Effects) ---
            if value == 1: # Only if checked (True)
                reason = None
                if column == "Newsletter":
                    reason = "Newsletter Check (7 Tage)"
                elif column == "Warenkorb":
                    reason = "Warenkorb Check (7 Tage)"
                
                if reason:
                    due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
                    c.execute(
                        "UPDATE leads SET follow_up_date = ?, follow_up_reason = ?, follow_up_status = 'pending' WHERE id = ?",
                        (due_date, reason, lead_id)
                    )
            # --------------------------------------
            
        conn.commit()
        return True
    except Exception as e:
        print(f"Update error: {e}")
        return False
    finally:
        conn.close()

def get_dashboard_stats(user_id):
    conn = get_connection()
    c = conn.cursor()
    
    stats = {}
    
    # Total Leads
    c.execute("SELECT COUNT(*) FROM leads WHERE user_id = ?", (user_id,))
    stats["total_leads"] = c.fetchone()[0]
    
    # Newsletter Signups
    c.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND newsletter_signup = 1", (user_id,))
    stats["newsletter_signups"] = c.fetchone()[0]
    
    # Emails Sent
    c.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND email_sent = 1", (user_id,))
    stats["emails_sent"] = c.fetchone()[0]
    
    # Responses
    c.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND response_received = 1", (user_id,))
    stats["responses"] = c.fetchone()[0]
    
    # Conversions
    c.execute("SELECT COUNT(*) FROM leads WHERE user_id = ? AND converted = 1", (user_id,))
    stats["conversions"] = c.fetchone()[0]
    
    # Top Keywords
    c.execute("SELECT keyword, COUNT(*) as count FROM searches WHERE user_id = ? GROUP BY keyword ORDER BY count DESC LIMIT 5", (user_id,))
    stats["top_keywords"] = c.fetchall()
    
    conn.close()
    return stats

def get_searches(user_id):
    conn = get_connection()
    query = "SELECT id, keyword, country, num_leads, category, timestamp FROM searches WHERE user_id = ? ORDER BY timestamp DESC"
    df = pd.read_sql_query(query, conn, params=(user_id,))
    conn.close()
    return df

def update_search_category(search_id, category):
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE searches SET category = ? WHERE id = ?", (category, search_id))
    conn.commit()
    conn.close()
