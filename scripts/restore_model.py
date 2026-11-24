"""Rebuild the compressed model file from repository text shards when needed."""
from __future__ import annotations
import base64
from pathlib import Path

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"

def restore_model() -> Path:
    target = MODEL_DIR / "model.joblib"
    if target.exists():
        return target
    parts = sorted(MODEL_DIR.glob("model.joblib.part*.b64"))
    if not parts:
        raise FileNotFoundError("models/model.joblib не табылды; restore shard файлдары жоқ.")
    encoded = "".join(part.read_text(encoding="ascii").strip() for part in parts)
    data = base64.b64decode(encoded, validate=True)
    temporary = target.with_suffix(".joblib.tmp")
    temporary.write_bytes(data)
    temporary.replace(target)
    return target

if __name__ == "__main__":
    print(f"Model restored: {restore_model()}")