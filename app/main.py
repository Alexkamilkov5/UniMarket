from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

app = FastAPI(title="UniMarket", version="0.1.0")


@app.get("/health")  # type: ignore[misc]
def health() -> dict[str, str]:
    return {"status": "ok"}


class HelloResponse(BaseModel):
    message: str = Field(..., examples=["Hello, Alice!"])


@app.get("/hello")  # type: ignore[misc]
def hello(name: str = Query("world")) -> dict[str, str]:
    return {"message": f"Hello, {name}!"}
