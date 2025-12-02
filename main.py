import pandas as pd
import requests
import io
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Your Google Sheet CSV URL
SHEET_ID = "1zZ0InMjFnxg3v1V5vBUtW4LAv36ns-D6w7zh9XtxzwY"
GID = "0"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"


# ---------------------------
# CLEAN + NORMALIZE CSV DATA
# ---------------------------
def load_sheet_data():
    """Fetch Google Sheet and return CLEAN + NORMALIZED rows"""

    # Fetch CSV
    res = requests.get(CSV_URL)
    raw_csv = res.text

    # Read CSV using pandas (handles commas inside cells correctly)
    df = pd.read_csv(io.StringIO(raw_csv))

    # Strip whitespace from headers
    df.columns = [str(c).strip() for c in df.columns]

    # Replace NaN with empty strings
    df = df.fillna("")

    # Convert to list of dicts
    rows = df.to_dict(orient="records")

    # Get all keys that appear in any row
    all_keys = set()
    for r in rows:
        all_keys.update(r.keys())

    # Normalize rows so every row has every column
    normalized_rows = []
    for r in rows:
        clean_row = {key: r.get(key, "") for key in all_keys}
        normalized_rows.append(clean_row)

    return normalized_rows


@app.get("/")
def home():
    return {"message": "ERP Score API is running ✔"}


@app.get("/erp/data")
def get_data():
    rows = load_sheet_data()
    return {
        "count": len(rows),
        "rows": rows
    }


@app.get("/erp/stats")
def get_stats():
    rows = load_sheet_data()

    # Compute average overall score
    scores = []
    for r in rows:
        try:
            scores.append(float(r.get("Overall Score", 0)))
        except:
            pass

    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    return {
        "total_clients": len(rows),
        "average_overall_score": avg_score,
    }
