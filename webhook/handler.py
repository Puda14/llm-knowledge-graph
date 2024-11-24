from fastapi import FastAPI, Request
from pymongo import MongoClient, errors
import os
import json

app = FastAPI()

def get_mongo_client():
  mongo_uri = os.getenv("MONGODB_URI")
  client = MongoClient(mongo_uri)
  try:
    client.admin.command("ping")
    print("Connected to MongoDB successfully!")
  except errors.ConnectionError as e:
    print("Failed to connect to MongoDB:", e)
    raise e
  return client

client = get_mongo_client()
db = client["Github-Webhook"]

@app.post("/github-webhook")
async def github_webhook(request: Request):
  payload = await request.json()

  result = db.github_events.insert_one(payload)
  print(f"Inserted document with id: {result.inserted_id}")

  return {"status": "success", "message": "Event received and stored"}
