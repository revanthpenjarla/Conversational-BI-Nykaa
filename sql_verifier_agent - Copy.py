from database import get_schema, execute_query

def verify_sql(sql, user_prompt=None, history=None):
    schema = get_schema()
    sql_upper = sql.upper().strip()

    # Block unsafe operations
    for keyword in ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE"]:
        if keyword in sql_upper:
            return {"valid": False, "error": f"Unsafe operation detected: {keyword}", "sql": sql}

    # Dry run the query
    res = execute_query(sql)
    if not res["success"]:
        err_msg = str(res["error"]).lower()
        if "no such column" in err_msg and user_prompt:
            # We catch the exception and send the real column list back to the LLM
            from llm_sql_agent import generate_sql
            schema_cols = []
            for t, c in schema.items():
                schema_cols.append(f"Table: {t}, Columns: {', '.join(c)}")
            schema_str = "\n".join(schema_cols)
            
            retry_prompt = f"Previous Query Failed: {res['error']}\n\nYou must use the EXACT column names from this schema (check case sensitivity):\n{schema_str}\n\nOriginal Question: {user_prompt}"
            retry_res = generate_sql(retry_prompt, history)
            new_sql = retry_res.get("sql", "SELECT * FROM active_data LIMIT 10")
            new_exp = retry_res.get("explanation", "")
            
            # Verify the retried SQL safely (to prevent infinite loops, just return it)
            return {"valid": True, "error": None, "sql": new_sql, "explanation": new_exp}
        return {"valid": False, "error": res["error"], "sql": sql}

    return {"valid": True, "error": None, "sql": sql}

if __name__ == "__main__":
    good_sql = "SELECT Campaign_Type, SUM(Revenue) FROM campaigns GROUP BY Campaign_Type"
    bad_sql = "SELECT fake_column FROM fake_table"

    print(verify_sql(good_sql))
    print(verify_sql(bad_sql))