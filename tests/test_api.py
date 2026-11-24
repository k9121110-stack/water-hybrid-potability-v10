import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from api import main
from src.rules import FEATURES

class StubModel:
    def predict_proba(self,frame): return [[.2,.8]]
def good_payload():
    row={k:1.0 for k in FEATURES}; row.update({"ph":7.2,"Chloramines":1.0,"Turbidity":.5}); return row
def setup(monkeypatch,tmp_path):
    monkeypatch.setattr(main,"LOG_DB",tmp_path/"log.sqlite3")
    monkeypatch.setattr(main,"get_artifact",lambda:{"model":StubModel(),"threshold":.5,"review_margin":.05,"feature_importance":{"ph":.2}})
    return TestClient(main.app)

def test_health_endpoint(monkeypatch,tmp_path):
    client=setup(monkeypatch,tmp_path); assert client.get("/health").status_code==200
def test_predict_endpoint(monkeypatch,tmp_path):
    client=setup(monkeypatch,tmp_path); res=client.post("/predict",json=good_payload()); assert res.status_code==200 and res.json()["decision"]=="potable_screening"
def test_explain_returns_rules_and_features(monkeypatch,tmp_path):
    client=setup(monkeypatch,tmp_path); res=client.post("/explain",json=good_payload()); assert "important_features" in res.json()
def test_api_rejects_wrong_type(monkeypatch,tmp_path):
    client=setup(monkeypatch,tmp_path); payload=good_payload(); payload["ph"]="not-a-number"; assert client.post("/predict",json=payload).status_code==422
def test_api_rejects_impossible_ph(monkeypatch,tmp_path):
    client=setup(monkeypatch,tmp_path); payload=good_payload(); payload["ph"]=20; assert client.post("/predict",json=payload).status_code==422
def test_api_logs_decision(monkeypatch,tmp_path):
    import sqlite3
    client=setup(monkeypatch,tmp_path); client.post("/predict",json=good_payload())
    with sqlite3.connect(tmp_path/"log.sqlite3") as db: assert db.execute("select count(*) from decisions").fetchone()[0]==1
