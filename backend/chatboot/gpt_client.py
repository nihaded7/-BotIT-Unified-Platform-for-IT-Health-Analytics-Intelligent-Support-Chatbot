from pathlib import Path
from dotenv import load_dotenv
import os
import requests

# Correct path: project root
env_path = Path(__file__).parent.parent.parent / ".env"
if not env_path.exists():
    raise FileNotFoundError(f"❌ .env file not found at: {env_path}")

load_dotenv(dotenv_path=env_path)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ No API key found. Make sure .env file contains OPENAI_API_KEY.")

GITHUB_API_URL = os.getenv(
    "GITHUB_API_URL",
    "https://models.inference.ai.azure.com/chat/completions",
)

def ask_gpt(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }

    response = requests.post(GITHUB_API_URL, headers=headers, json=payload)

    if response.status_code != 200:
        raise RuntimeError(f"❌ API call failed: {response.status_code} {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]
