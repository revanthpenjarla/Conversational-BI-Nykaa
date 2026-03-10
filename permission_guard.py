import re

def check_permission(sql):
    sql_upper = sql.upper().strip()

    # Task 2: Strict regex word boundary check to prevent bypasses
    # Blocks DROP, TRUNCATE, ALTER, DELETE, UPDATE, INSERT entirely
    forbidden_pattern = re.compile(r'\b(DROP|TRUNCATE|ALTER|DELETE|UPDATE|INSERT)\b')
    
    match = forbidden_pattern.search(sql_upper)
    if match:
        return {"allowed": False, "reason": f"UNAUTHORIZED OPERATION: The '{match.group(1)}' command is strictly prohibited."}

    return {"allowed": True, "reason": "OK"}

if __name__ == "__main__":
    print(check_permission("SELECT * FROM campaigns"))
    print(check_permission("DROP TABLE campaigns"))
    print(check_permission("DELETE FROM campaigns"))
    print(check_permission("DELETE FROM campaigns WHERE Campaign_ID = '1'"))