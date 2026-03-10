from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import sqlite3
import io
import csv
import re
import os
import shutil
from llm_sql_agent import generate_sql, generate_insight
from sql_verifier_agent import verify_sql
from permission_guard import check_permission
from database import execute_query, get_live_schema, DB_PATH
from conversation_memory import get_history, add_to_history
from chart_selector_agent import select_chart

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class DashboardRequest(BaseModel):
    prompt: str
    session_id: str = "default"

@app.post("/generate-dashboard")
async def generate_dashboard(req: DashboardRequest):
    try:
        # Pre-Flight Check: Ensure data is uploaded
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='active_data';")
        table_exists = cursor.fetchone()
        conn.close()

        if not table_exists:
            return {"success": False, "error": "No data uploaded. Please upload a CSV or Excel file first."}

        history = get_history(req.session_id)
        llm_response = generate_sql(req.prompt, history)
        sql = llm_response.get("sql", "SELECT * FROM active_data")
        explanation = llm_response.get("explanation", "")

        verify = verify_sql(sql, req.prompt, history)
        if not verify["valid"]:
            return {"success": False, "error": verify["error"]}

        sql = verify.get("sql", sql)
        if "explanation" in verify and verify["explanation"]:
            explanation = verify["explanation"]

        permission = check_permission(sql)
        if not permission["allowed"]:
            return {"success": False, "error": permission["reason"]}

        result = execute_query(sql)
        if not result["success"]:
            err_msg = str(result["error"]).lower()
            if "no such column" in err_msg:
                live_cols = get_live_schema()
                return {"success": False, "error": f"Column mismatch. The active dataset only contains: {', '.join(live_cols)}"}
            return {"success": False, "error": result["error"]}

        add_to_history(req.session_id, req.prompt, sql)

        chart_type = select_chart(result["columns"], result["data"])
        
        # Insight Agent (Top 5 rows only)
        insight = ""
        if result["data"]:
            insight = generate_insight(result["data"][:5])

        return {
            "success": True,
            "sql": sql,
            "explanation": explanation,
            "insight": insight,
            "chart_type": chart_type,
            "columns": result["columns"],
            "data": result["data"],
            "summary": "Here are the insights successfully retrieved from your Nykaa database.",
            "verified": verify["valid"]
        }

    except Exception as e:
        return {"success": False, "error": str(e)}

def load_csv_to_db(file_path):
    try:
        # 0a. Data Purge
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DROP TABLE IF EXISTS active_data")
        conn.commit()
        conn.close()

        df = None
        detected_format = "CSV"

        # 0b. Binary Block (Check for Zip/Excel 'PK' signature)
        is_excel = False
        if file_path.lower().endswith(('.xlsx', '.xls')):
            is_excel = True
            detected_format = "Excel"
        else:
            with open(file_path, 'rb') as f:
                if f.read(2) == b'PK':
                    is_excel = True
                    detected_format = "Excel"

        if is_excel:
            df = pd.read_excel(file_path)
        else:
            # 1. Robust File Opening & Multi-Encoding Fallback
            try:
                # Use C-engine sniffer with BOM support
                df = pd.read_csv(file_path, sep=None, engine='python', on_bad_lines='warn', quoting=csv.QUOTE_MINIMAL, encoding='utf-8-sig')
            except Exception:
                df = pd.read_csv(file_path, sep=None, engine='python', on_bad_lines='warn', quoting=csv.QUOTE_MINIMAL, encoding='ISO-8859-1')

        if df is None or df.empty:
            return {"success": False, "error": "File is empty or could not be parsed."}

        # Verification Step
        print(f"Detected Columns: {df.columns.tolist()}")
        if len(df.columns) <= 1:
             return {"success": False, "error": "CSV Parsing Error: Only one column detected. Please check your file delimiter."}

        # Column Name Sanitizer - Strip all hidden whitespaces absolutely
        df.columns = [str(c).strip() for c in df.columns]

        # Ensure purely alphanumeric columns + no leading digits for SQLite
        clean_cols = []
        for c in df.columns:
            c_str = str(c).replace('\0', '').replace('\ufeff', '').strip()
            c_str = re.sub(r'\W+', '_', c_str) 
            if c_str and c_str[0].isdigit():
                c_str = 'col_' + c_str
            if not c_str:
                c_str = 'unnamed_col'
            clean_cols.append(c_str)
        df.columns = clean_cols
        
        # 3. Text-Only Validation & Cell Sanitization
        sample_rows = df.head(5).astype(str).values.flatten()
        if len(sample_rows) > 0:
            sample_text = "".join(sample_rows)
            non_ascii_count = sum(1 for char in sample_text if ord(char) > 127)
            if len(sample_text) > 0 and (non_ascii_count / len(sample_text)) > 0.5:
                return {"success": False, "error": "File encoding mismatch or corrupted binary data."}

        # Replace NUL bytes in data
        df = df.replace('\0', '', regex=True)

        # 4. The Active Data Contract
        conn = sqlite3.connect(DB_PATH)
        df.to_sql("active_data", conn, if_exists="replace", index=False)
        conn.close()
        
        return {
            "success": True, 
            "row_count": len(df),
            "columns": list(df.columns),
            "format_msg": f"{detected_format} file processed successfully"
        }
    except Exception as e:
        return {"success": False, "error": f"Failed to load CSV: {str(e)}"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    temp_file_path = os.path.abspath("temp_upload.tmp")
    try:
        # Save uploaded file to temp path using shutil
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        result = load_csv_to_db(temp_file_path)
        
        if result["success"]:
            result["filename"] = file.filename
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}
    finally:
        # Cleanup temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

@app.get("/")
def root():
    return {"status": "Conversational BI running"}