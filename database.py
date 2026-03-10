import sqlite3

DB_PATH = "nykaa.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_live_schema():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(active_data);")
    columns = cursor.fetchall()
    conn.close()
    return [col[1] for col in columns]

def get_schema():
    conn = get_connection()
    cursor = conn.cursor()
    
    schema = {}
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_data';")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        schema[table_name] = [col[1] for col in columns]
    
    conn.close()
    return schema

def execute_query(sql):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()
        return {"success": True, "data": [dict(zip(columns, row)) for row in rows], "columns": columns}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    schema = get_schema()
    print("Schema:", schema)
