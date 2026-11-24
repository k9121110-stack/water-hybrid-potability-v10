from pathlib import Path
import sys, json, sqlite3
from datetime import datetime, timezone
from typing import Optional
import joblib
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.decision import decide

ROOT=Path(__file__).resolve().parents[1]
LOG_DB=ROOT/"decision_log.sqlite3"
app=FastAPI(title="Ауыз су сапасын скринингтеу",version="1.0.0")
class WaterSample(BaseModel):
    ph: Optional[float]=None
    Hardness: Optional[float]=None
    Solids: Optional[float]=None
    Chloramines: Optional[float]=None
    Sulfate: Optional[float]=None
    Conductivity: Optional[float]=None
    Organic_carbon: Optional[float]=None
    Trihalomethanes: Optional[float]=None
    Turbidity: Optional[float]=None

def get_artifact():
    path=ROOT/"models"/"model.joblib"
    if not path.exists(): raise HTTPException(status_code=503,detail="Colab-та модельді оқытып, models/model.joblib файлын салыңыз.")
    return joblib.load(path)

def log_decision(endpoint,payload,result):
    with sqlite3.connect(LOG_DB) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS decisions
          (id INTEGER PRIMARY KEY, created_at TEXT, endpoint TEXT, input_json TEXT, decision TEXT, source TEXT, result_json TEXT)""")
        source="rules" if result["decision"]=="invalid_input" else ("model+rules" if result.get("fired_rules") else "model")
        db.execute("INSERT INTO decisions(created_at,endpoint,input_json,decision,source,result_json) VALUES(?,?,?,?,?,?)",
          (datetime.now(timezone.utc).isoformat(),endpoint,json.dumps(payload,ensure_ascii=False),result["decision"],source,json.dumps(result,ensure_ascii=False)))

@app.get("/health")
def health(): return {"status":"ok","model_ready":(ROOT/"models"/"model.joblib").exists()}

def run(sample,endpoint):
    payload=sample.model_dump()
    result=decide(payload,get_artifact())
    log_decision(endpoint,payload,result)
    if result["decision"]=="invalid_input": raise HTTPException(status_code=422,detail=result)
    return result

@app.post("/predict")
def predict(sample:WaterSample): return run(sample,"/predict")

@app.post("/explain")
def explain(sample:WaterSample): return run(sample,"/explain")
