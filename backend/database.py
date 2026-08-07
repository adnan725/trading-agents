import json
import sqlite3
 
DB = "accounts.db"
INITIAL_BALANCE = 10_000.0
 
 
def init_db(db=DB):
    """Create the table if it doesn't exist. Safe to call on every startup."""
    with sqlite3.connect(db) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                name    TEXT PRIMARY KEY,
                account TEXT NOT NULL
            )
        """)
        conn.commit()
 
 
def write_account(name, account_dict, db=DB):
    """Insert or update an account. `account_dict` is stored as JSON."""
    json_data = json.dumps(account_dict)
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO accounts (name, account)
            VALUES (?, ?)
            ON CONFLICT(name) DO UPDATE SET account=excluded.account
        """, (name.lower(), json_data))
        conn.commit()
 
 
def read_account(name, db=DB):
    """Return the account dict, or None if the name isn't stored."""
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT account FROM accounts WHERE name = ?", (name.lower(),))
        row = cursor.fetchone()
    return json.loads(row[0]) if row else None
 
 
def list_accounts(db=DB):
    """Return every stored name."""
    with sqlite3.connect(db) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM accounts ORDER BY name")
        return [r[0] for r in cursor.fetchall()]
 
 
def delete_account(name, db=DB):
    with sqlite3.connect(db) as conn:
        conn.execute("DELETE FROM accounts WHERE name = ?", (name.lower(),))
        conn.commit()
 
 
def create_account(name, db=DB):
    """Create a fresh account with default fields."""
    fields = {
        "name": name.lower(),
        "balance": INITIAL_BALANCE,
        "strategy": "",
        "holdings": {},
        "transactions": [],
        "portfolio_value_time_series": [],
    }
    write_account(name, fields, db=db)
    return fields
 
 
if __name__ == "__main__":
    init_db()
    create_account("Adnan")
    print(read_account("adnan"))