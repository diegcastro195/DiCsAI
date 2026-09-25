import sqlite3

conn = sqlite3.connect("orders.db")
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT,
        tipo TEXT,
        direccion TEXT,
        items TEXT,
        total INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )
""")

conn.commit()
conn.close()
print("Database ready: orders.db")

