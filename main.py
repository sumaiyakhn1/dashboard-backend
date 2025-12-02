from fastapi import FastAPI
import requests, csv, io

app = FastAPI()

SHEET_ID = "1zZ0InMjFnxg3v1V5vBUtW4LAv36ns-D6w7zh9XtxzwY"
GID = "0"  # your real gid

CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"


def fetch_sheet():
    """Fetch Google Sheet CSV and convert to JSON array."""
    res = requests.get(CSV_URL)
    text = res.text

    f = io.StringIO(text)
    reader = csv.DictReader(f)

    rows = []
    for row in reader:
        clean = {k.strip(): v.strip() for k, v in row.items()}
        rows.append(clean)

    return rows


@app.get("/")
def home():
    return {"message": "ERP Score Backend Running ✔"}


@app.get("/erp/data")
def erp_data():
    rows = fetch_sheet()
    return {"count": len(rows), "rows": rows}


@app.get("/erp/stats")
def erp_stats():
    rows = fetch_sheet()

    # Example calculation
    scores = []
    for r in rows:
        try:
            scores.append(float(r.get("Overall Score", 0)))
        except:
            pass

    avg_score = round(sum(scores) / len(scores), 2) if scores else 0

    return {
        "total_clients": len(rows),
        "average_overall_score": avg_score
    }
