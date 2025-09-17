from typing import Dict

from fastapi import FastAPI

app = FastAPI(title="UniMarket", version="0.1.0")


@app.get("/health")  # type: ignore[misc]
def health() -> Dict[str, str]:
    return {"status": "ok"}
