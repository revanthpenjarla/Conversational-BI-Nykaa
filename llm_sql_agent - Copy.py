from google import genai
from google.genai import types
import os
import json
import sqlite3
from dotenv import load_dotenv
from database import DB_PATH, get_live_schema

load_dotenv()

# Initialize the Gemini Client
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options=types.HttpOptions(api_version="v1")
)

def generate_sql(user_prompt, conversation_history=[]):
    """
    Updated to accept conversation_history to match main.py
    """
    # 1. Fetch the schema dynamically via live hook
    live_columns = get_live_schema()
    live_cols_str = ", ".join(live_columns)
    
    # 2. Format the history for the prompt
    history_str = "\n".join(conversation_history[-5:]) if conversation_history else "None"

    # 3. Build the prompt
    prompt_text = f"""
You are a specialized Text-to-SQL translator for a Marketing BI tool.

Table Name: Always use active_data.

DANGER: The active_data table ONLY has these columns: {live_cols_str}. You MUST use these exact names, including their casing. Do not guess names like 'Language' if the table says 'language'.

Smart Aggregation: If the user asks for 'revenue' but it's a category comparison, always use SUM(Revenue).

Date Handling: If the user mentions a date, use WHERE Date LIKE '%DD-MM-YYYY%'.

JSON Response: Return a JSON object with two keys: sql (the query) and explanation (a 1-sentence plain English summary of what the query does).

CONVERSATION HISTORY:
{history_str}

USER QUESTION:
{user_prompt}
"""

    # 4. Generate content using the working model
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text
    )
    
    if response and response.text:
        try:
            # Clean markdown code blocks if the LLM wraps the JSON
            clean_json = response.text.replace('```json', '').replace('```', '').strip()
            data = json.loads(clean_json)
            return data
        except Exception as e:
            # Fallback for parsing errors
            return {"sql": "SELECT * FROM active_data LIMIT 10", "explanation": "Failed to parse JSON generation. Returning safe default."}
    else:
        return {"sql": "SELECT * FROM active_data LIMIT 10", "explanation": "Fallback default query."}

def generate_insight(data_sample):
    prompt_text = f"Based on this data: {data_sample}, give a 1-sentence business insight."
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt_text
    )
    if response and response.text:
        return response.text.strip()
    return "No insights available."

if __name__ == "__main__":
    try:
        # Test with the two arguments main.py uses
        sql = generate_sql("Show total revenue by campaign type", [])
        print("--- GENERATED SQL ---")
        print(sql)
    except Exception as e:
        print(f"❌ Error: {e}")