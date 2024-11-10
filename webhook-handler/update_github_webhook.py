import requests
import json
import os
import time
from dotenv import load_dotenv

load_dotenv()

def get_ngrok_url():
  """Fetch the public URL from Ngrok's local API."""
  try:
    response = requests.get("http://localhost:4040/api/tunnels")
    response.raise_for_status()
    tunnels = response.json()["tunnels"]
    public_url = tunnels[0]["public_url"]
    return public_url
  except Exception as e:
    print(f"Failed to fetch Ngrok URL: {e}")
    return None

def update_github_webhook(ngrok_url):
  """Update GitHub webhook with the new Ngrok URL."""
  owner = "Puda14"
  repo = "Github-Webhook"
  webhook_id = "512322882"

  github_api_url = f"https://api.github.com/repos/{owner}/{repo}/hooks/{webhook_id}"
  headers = {
    "Authorization": f"token {os.getenv('GITHUB_TOKEN')}",
    "Content-Type": "application/json"
  }
  payload = {
    "config": {
      "url": f"{ngrok_url}/github-webhook",
      "content_type": "json"
    }
  }
  try:
    response = requests.patch(github_api_url, headers=headers, data=json.dumps(payload))
    if response.status_code == 200:
      print("GitHub webhook updated successfully!")
    else:
      print(f"Failed to update GitHub webhook: {response.status_code}, {response.text}")
  except Exception as e:
    print(f"Error updating GitHub webhook: {e}")

if __name__ == "__main__":
  time.sleep(5)
  ngrok_url = get_ngrok_url()
  if ngrok_url:
    update_github_webhook(ngrok_url)
