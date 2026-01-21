#!/usr/bin/env python3
"""
AI Support Request Processor
Polls Notion database for new requests and generates AI responses
"""

import os
import requests
from openai import OpenAI
from datetime import datetime

# Config
NOTION_TOKEN = os.environ.get("REFURBED_NOTION_TOKEN")
OPENAI_KEY = os.environ.get("REFURBED_OPENAI_API_KEY")
DATABASE_ID = "a4db05f8-fdd2-40a6-9f26-39a7815af653"

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

openai_client = OpenAI(api_key=OPENAI_KEY)

def get_ai_response(customer_question, title):
    """Generate a professional support response using AI"""
    prompt = f"""You are a friendly customer support agent for Refurbed, a company selling refurbished electronics.

Customer Request: {title}

Customer Message:
{customer_question}

Generate a professional, empathetic response in the same language as the customer.
Include:
1. Acknowledge their concern
2. Provide helpful information or next steps
3. Offer to help further

Keep it concise (under 200 words).

Also provide at the end:
- Sentiment: (Positive/Neutral/Frustrated/Angry)
- Category: (Delivery/Returns/Product Quality/Billing/General)
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )
    return response.choices[0].message.content

def query_database():
    """Get all pages from database"""
    response = requests.post(
        f"https://api.notion.com/v1/databases/{DATABASE_ID}/query",
        headers=headers,
        json={}
    )
    return response.json().get("results", [])

def get_page_blocks(page_id):
    """Get blocks from a page"""
    response = requests.get(
        f"https://api.notion.com/v1/blocks/{page_id}/children",
        headers=headers
    )
    return response.json().get("results", [])

def add_ai_response(page_id, ai_response):
    """Add AI response blocks to page"""
    requests.patch(
        f"https://api.notion.com/v1/blocks/{page_id}/children",
        headers=headers,
        json={
            "children": [
                {"object": "block", "type": "divider", "divider": {}},
                {
                    "object": "block",
                    "type": "callout",
                    "callout": {
                        "rich_text": [{"type": "text", "text": {"content": f"🤖 AI Draft Response ({datetime.now().strftime('%H:%M')})"}}],
                        "icon": {"emoji": "🤖"},
                        "color": "blue_background"
                    }
                },
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": ai_response}}]
                    }
                }
            ]
        }
    )

def process_requests():
    """Process new support requests"""
    print("\n" + "="*60)
    print("🔍 CHECKING FOR NEW SUPPORT REQUESTS")
    print("="*60)

    pages = query_database()
    print(f"📋 Found {len(pages)} items in database")

    processed = 0
    for page in pages:
        page_id = page["id"]

        # Get title
        title = "Untitled"
        for prop_name, prop in page.get("properties", {}).items():
            if prop.get("type") == "title":
                titles = prop.get("title", [])
                if titles:
                    title = titles[0].get("plain_text", "Untitled")
                break

        # Get page content
        blocks = get_page_blocks(page_id)
        has_ai = False
        question = ""

        for block in blocks:
            block_type = block.get("type")
            if block_type == "callout":
                texts = block.get("callout", {}).get("rich_text", [])
                for t in texts:
                    if "AI" in t.get("plain_text", ""):
                        has_ai = True
            elif block_type == "paragraph":
                texts = block.get("paragraph", {}).get("rich_text", [])
                for t in texts:
                    question += t.get("plain_text", "") + " "

        if has_ai:
            print(f"  ⏭️  '{title}' - Already has AI response")
            continue

        if not question.strip():
            print(f"  ⏭️  '{title}' - No question content yet")
            continue

        print(f"\n  📧 PROCESSING: '{title}'")
        print(f"     Question: {question[:80]}...")

        # Generate AI response
        print(f"     🤖 Generating AI response...")
        ai_response = get_ai_response(question.strip(), title)

        # Add to page
        add_ai_response(page_id, ai_response)
        print(f"     ✅ AI response added to Notion!")

        processed += 1

    print("\n" + "="*60)
    print(f"✅ DONE - Processed {processed} request(s)")
    print("="*60)
    return processed

if __name__ == "__main__":
    print("🚀 NOTION AI SUPPORT PROCESSOR")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    process_requests()
