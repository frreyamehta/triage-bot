import os
import secrets
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Header, HTTPException

from app import db
from app.schemas import IncomingMessage

load_dotenv()
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Triage Bot", lifespan=lifespan)


def verify_secret(provided: str | None) -> None:
    # compare_digest avoids timing attacks; real webhooks (Stripe, GitHub) sign requests similarly
    if not WEBHOOK_SECRET or not provided or not secrets.compare_digest(provided, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


@app.post("/webhook", status_code=201)
def receive_message(msg: IncomingMessage, x_webhook_secret: str | None = Header(default=None)):
    verify_secret(x_webhook_secret)
    message_id = db.insert_message(msg.sender, msg.channel, msg.text)
    return {"id": message_id, "status": "received"}


@app.get("/messages")
def list_messages(limit: int = 50):
    return db.list_messages(limit)


@app.get("/messages/{message_id}")
def get_message(message_id: int):
    row = db.get_message(message_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return row