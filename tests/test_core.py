import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.rules import FEATURES,inspect_input
from src.decision import decide

class StubModel:
    def __init__(self,p): self.p=p
    def predict_proba(self,frame): return [[1-self.p,self.p]]
def sample(**updates):
    row={k:1.0 for k in FEATURES}; row.update({"ph":7.2,"Chloramines":1.0,"Turbidity":0.5}); row.update(updates); return row
def artifact(p=.8,threshold=.5,margin=.05): return {"model":StubModel(p),"threshold":threshold,"review_margin":margin}

def test_positive_screening(): assert decide(sample(),artifact())["decision"]=="potable_screening"
def test_negative_screening(): assert decide(sample(),artifact(.2))["decision"]=="not_potable_screening"
def test_threshold_margin_requests_review(): assert decide(sample(),artifact(.51))["decision"]=="manual_review"
def test_ph_advisory(): assert "R14" in [x["rule_id"] for x in inspect_input(sample(ph=9))[1]]
def test_missing_ph_allowed_and_flagged(): assert not inspect_input(sample(ph=None))[0]
def test_negative_sulfate_blocked(): assert inspect_input(sample(Sulfate=-1))[0][0]["rule_id"]=="R05"
def test_ph_above_scale_blocked(): assert inspect_input(sample(ph=15))[0][0]["rule_id"]=="R01"
def test_nan_blocked(): assert inspect_input(sample(ph=float("nan")))[0]
def test_unknown_field_blocked(): assert inspect_input({**sample(),"other":1})[0]
def test_non_numeric_blocked(): assert inspect_input(sample(ph="bad"))[0]
def test_high_turbidity_routes_to_review(): assert decide(sample(Turbidity=2),artifact(.9))["decision"]=="manual_review"
def test_high_chloramine_routes_to_review(): assert decide(sample(Chloramines=4),artifact(.9))["decision"]=="manual_review"
def test_advisory_appears_in_result(): assert decide(sample(ph=9),artifact(.9))["fired_rules"]
def test_all_missing_supported(): assert decide({k:None for k in FEATURES},artifact(.2))["decision"]=="not_potable_screening"
def test_exact_threshold_requests_review(): assert decide(sample(),artifact(.5))["decision"]=="manual_review"
