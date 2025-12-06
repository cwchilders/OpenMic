import sqlite3

db_folder = "/home/bill/local_projects/tonex/data"
db_file = db_folder + "/Library.db"

db = sqlite3.connect(db_file)
cursor = db.cursor()

# Dump complete schema
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for table_def in cursor.fetchall():
    print(table_def[0])
    print("\n")

# For each table, get a sample row to see data types
for table in ['Presets', 'ToneModels', 'ImpulseResponses']:
    cursor.execute(f"SELECT * FROM {table} LIMIT 1")
    row = cursor.fetchone()
    cursor.execute(f"PRAGMA table_info({table})")
    cols = cursor.fetchall()
    
    print(f"\n{table}:")
    for i, col in enumerate(cols):
        col_name = col[1]
        col_type = col[2]
        sample_val = row[i] if row else None
        print(f"  {col_name} ({col_type}): {sample_val}")