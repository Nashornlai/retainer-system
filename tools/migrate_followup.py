
import sqlite3

DB_PATH = "leads.db"

def migrate_followup():
    print(f"Migrating {DB_PATH} for Follow-up System...")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    columns = [
        ("follow_up_date", "TEXT"),
        ("follow_up_reason", "TEXT"),
        ("follow_up_status", "TEXT DEFAULT 'pending'")
    ]
    
    for col, dtype in columns:
        try:
            c.execute(f"ALTER TABLE leads ADD COLUMN {col} {dtype}")
            print(f"✅ Added {col}")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e):
                print(f"ℹ️ {col} already exists.")
            else:
                print(f"❌ Error adding {col}: {e}")
                
    conn.commit()
    conn.close()
    print("Migration completed.")

if __name__ == "__main__":
    migrate_followup()
