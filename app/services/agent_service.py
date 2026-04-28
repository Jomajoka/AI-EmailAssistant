import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv
import re

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
MODEL_NAME = os.getenv("LLM_MODEL")

ALLOWED_CATEGORIES = [
    "Work", "Personal", "Promotional",
    "Finance", "Travel", "Social", "Other"
]

ALLOWED_PRIORITIES = ["High", "Medium", "Low"]


def build_prompt(subject, body, reference_date,sender):
    return f"""
You are an AI assistant that extracts structured productivity information from emails.

The email was received on: {reference_date}

Return ONLY valid JSON. Do NOT include explanations.
Do NOT wrap the response in markdown.
Do NOT add commentary.

Use this exact schema:

{{
  "summary": "string",
  "category": "Work | Personal | Promotional | Finance | Travel | Social | Other",
  "priority": "High | Medium | Low",
  "tasks": [
    {{
      "title": "string",
      "description": "string or null",
      "due_date": "YYYY-MM-DD or null"
      "priority": "High | Medium | Low" 
    }}
  ],
  "meetings": [
    {{
      "title": "string",
      "meeting_date": "YYYY-MM-DD",
      "start_time": "HH:MM or null",
      "end_time": "HH:MM or null",
      "description": "string or null"
    }}
  ]
}}

Rules:
- If no tasks, return empty list []
- If no meetings, return empty list []
- Convert all dates to YYYY-MM-DD
- Convert times to 24-hour HH:MM
- If year missing, assume current year
- If date cannot be determined, use null
- Only extract real actionable tasks, be sure to distinguish promotional content from real tasks, check the email sender to see if they are a commercial entity and decide if it is promotional
- Only extract meetings if clearly scheduled
- If participants (Organization or Individual or Team) are mentioned or sender is specified, format description like:
  "Meeting with <participants> regarding <context>"


Email Subject:
{subject}

Email Body:
{body}

Email Sender:
{sender}
"""


def clean_json_response(text):
    text = text.strip()

    # Remove markdown fences like ```json or ```
    text = re.sub(r"```[a-zA-Z]*", "", text)
    text = text.replace("```", "")

    # 🔥 Remove leading "json" if present
    if text.lower().startswith("json"):
        text = text[4:].strip()

    # Extract first JSON object
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def validate_output(data):
    if data.get("category") not in ALLOWED_CATEGORIES:
        data["category"] = "Other"

    if data.get("priority") not in ALLOWED_PRIORITIES:
        data["priority"] = "Low"

    if not isinstance(data.get("tasks"), list):
        data["tasks"] = []

    if not isinstance(data.get("meetings"), list):
        data["meetings"] = []

    for task in data["tasks"]:
        if task.get("priority") not in ALLOWED_PRIORITIES:
            task["priority"] = "Medium"

    return data


def extract_email_intelligence(subject, body, received_at,sender):
    if isinstance(received_at, datetime):
        reference_date = received_at.strftime("%Y-%m-%d")
    else:
        reference_date = received_at.split(" ")[0]
    prompt = build_prompt(subject, body, reference_date,sender)

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "http://localhost",
        "X-Title": "EmailAssist",     
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload
    )

    response.raise_for_status()

    result_text = response.json()["choices"][0]["message"]["content"]
    cleaned = clean_json_response(result_text)

    print("🔍 CLEANED JSON:", cleaned)

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        raise Exception("LLM did not return valid JSON.")

    validated = validate_output(parsed)

    return validated