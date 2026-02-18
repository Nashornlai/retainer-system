import sqlite3
import os

DB_FILE = "leads.db"

def fix_database():
    if not os.path.exists(DB_FILE):
        print("❌ Database file not found.")
        return

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    columns_to_add = [
        ("leads", "newsletter_signup", "BOOLEAN DEFAULT 0"),
        ("leads", "cart_abandoned", "BOOLEAN DEFAULT 0"),
        ("leads", "email_sent", "BOOLEAN DEFAULT 0"),
        ("leads", "response_received", "BOOLEAN DEFAULT 0"),
        ("leads", "converted", "BOOLEAN DEFAULT 0"),
        ("leads", "notes", "TEXT"),
        ("searches", "category", "TEXT")
    ]
    
    print("🔧 Fixing Database Schema...")
    
    for table, col, dtype in columns_to_add:
        try:
            c.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
            print(f"✅ Added column: {table}.{col}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print(f"ℹ️ Column already exists: {table}.{col}")
            else:
                print(f"❌ Error adding {table}.{col}: {e}")

    conn.commit()
    conn.close()
    print("🎉 Database fix complete.")

if __name__ == "__main__":
    fix_database()
