#!/usr/bin/env python3
"""
Create the Support Requests database in Notion
"""

import os
from notion_client import Client

notion = Client(auth=os.environ.get("REFURBED_NOTION_TOKEN"))

# Find the Teamspace Home page to use as parent
print("🔍 Finding parent page...")
results = notion.search(filter={"property": "object", "value": "page"})

parent_id = None
for page in results.get("results", []):
    if "properties" in page:
        for prop in page["properties"].values():
            if prop.get("type") == "title" and prop.get("title"):
                title = prop["title"][0]["plain_text"] if prop["title"] else ""
                if "Teamspace" in title or "Home" in title:
                    parent_id = page["id"]
                    print(f"✅ Found parent: {title}")
                    break

if not parent_id:
    # Use first available page
    parent_id = results["results"][0]["id"]
    print(f"✅ Using first available page as parent")

# Create the Support Requests database
print("\n📊 Creating Support Requests database...")

database = notion.databases.create(
    parent={"type": "page_id", "page_id": parent_id},
    title=[{"type": "text", "text": {"content": "🎫 AI Support Requests"}}],
    icon={"type": "emoji", "emoji": "🎫"},
    properties={
        "Request": {
            "title": {}
        },
        "Customer Question": {
            "rich_text": {}
        },
        "Status": {
            "select": {
                "options": [
                    {"name": "New", "color": "red"},
                    {"name": "Processing", "color": "yellow"},
                    {"name": "Done", "color": "green"}
                ]
            }
        },
        "AI Draft Response": {
            "rich_text": {}
        },
        "Sentiment": {
            "select": {
                "options": [
                    {"name": "😊 Positive", "color": "green"},
                    {"name": "😐 Neutral", "color": "gray"},
                    {"name": "😤 Frustrated", "color": "orange"},
                    {"name": "😡 Angry", "color": "red"}
                ]
            }
        },
        "Category": {
            "select": {
                "options": [
                    {"name": "Delivery", "color": "blue"},
                    {"name": "Returns", "color": "purple"},
                    {"name": "Product Quality", "color": "orange"},
                    {"name": "Billing", "color": "green"},
                    {"name": "General", "color": "gray"}
                ]
            }
        },
        "Created": {
            "created_time": {}
        }
    }
)

db_id = database["id"]
db_url = database["url"]

print(f"✅ Database created!")
print(f"   ID: {db_id}")
print(f"   URL: {db_url}")

# Save the database ID for later use
with open("/home/student/Projects/notion-ai-automation/.database_id", "w") as f:
    f.write(db_id)

print(f"\n📝 Database ID saved to .database_id")

# Add a sample request
print("\n➕ Adding sample support request...")

sample_page = notion.pages.create(
    parent={"database_id": db_id},
    properties={
        "Request": {"title": [{"text": {"content": "Order #12345 - Delivery Issue"}}]},
        "Customer Question": {"rich_text": [{"text": {"content": "Hallo, ich habe vor 2 Wochen ein iPhone 13 bestellt (Bestellnummer REF-2026-12345) aber das Paket ist immer noch nicht angekommen. DHL zeigt seit 5 Tagen 'In Transit' an. Können Sie mir bitte helfen? Ich brauche das Handy dringend für meine Arbeit!"}}]},
        "Status": {"select": {"name": "New"}}
    }
)

print(f"✅ Sample request added!")
print(f"\n🎉 Setup complete! Open Notion to see the database.")
print(f"   {db_url}")
