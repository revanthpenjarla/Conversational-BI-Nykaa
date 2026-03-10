import pandas as pd
import sqlite3
CSV_PATH = "nykaa_campaign_data.csv"
DB_PATH = "nykaa.db"
df = pd.read_csv(CSV_PATH)
print("Columns found:", df.columns.tolist())
print("Rows:", len(df))
print(df.head(3))
conn = sqlite3.connect(DB_PATH)
df.to_sql("campaigns", conn, if_exists="replace", index=False)
conn.close()
print("Done! nykaa.db created with campaigns table.")