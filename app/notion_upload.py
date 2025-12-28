import os
import re
from notion_client import Client
from config import NOTION_API_KEY, NOTION_PAGE_ID
import logging

# === CONFIG ===
notion = Client(auth=NOTION_API_KEY)

# === LOGGER ===
logger = logging.getLogger(__name__)

# === 1. Read summarized notes ===
def read_notes_file(topic_title, notes_folder):
    safe_title = topic_title.replace(" ", "_")
    path = os.path.join(notes_folder, f"{safe_title}.md")
    if not os.path.exists(path):
        raise FileNotFoundError(f"{path} not found")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
    
# === 2. Convert Markdown to Notion blocks (simplified) ===
def markdown_to_notion_blocks(md_text):
    blocks = []

    def rich_text(text):
        parts = []
        pattern = r"(\*\*[^*]+\*\*)"
        tokens = re.split(pattern, text)

        for token in tokens:
            if token.startswith("**") and token.endswith("**"):
                parts.append({
                    "type": "text",
                    "text": {"content": token[2:-2]},
                    "annotations": {"bold": True}
                })
            else:
                parts.append({
                    "type": "text",
                    "text": {"content": token}
                })
        return parts

    lines = md_text.split("\n")

    for line in lines:
        line = line.rstrip()

        if not line:
            continue

        # Horizontal rule
        if line.strip() == "---":
            blocks.append({
                "object": "block",
                "divider": {}
            })
            continue

        # Headings
        if line.startswith("#### "):
            blocks.append({
                "object": "block",
                "heading_3": {"rich_text": rich_text(line[5:])}
            })
            continue

        if line.startswith("### "):
            blocks.append({
                "object": "block",
                "heading_3": {"rich_text": rich_text(line[4:])}
            })
            continue

        if line.startswith("## "):
            blocks.append({
                "object": "block",
                "heading_2": {"rich_text": rich_text(line[3:])}
            })
            continue

        if line.startswith("# "):
            blocks.append({
                "object": "block",
                "heading_1": {"rich_text": rich_text(line[2:])}
            })
            continue

        # Bold-only numbered section → heading_3
        if re.match(r"\*\*\d+\..+\*\*", line):
            blocks.append({
                "object": "block",
                "heading_3": {"rich_text": rich_text(line.replace("**", ""))}
            })
            continue

        # Bullets (* or -)
        if line.lstrip().startswith(("* ", "- ")):
            blocks.append({
                "object": "block",
                "bulleted_list_item": {
                    "rich_text": rich_text(line.lstrip()[2:])
                }
            })
            continue

        # Paragraph
        blocks.append({
            "object": "block",
            "paragraph": {
                "rich_text": rich_text(line)
            }
        })

    return blocks

# === 3. Upload to Notion ===
def upload_to_notion(topic_title, notes_folder, logger, batch_size=100):
    md_text = read_notes_file(topic_title, notes_folder)
    blocks = markdown_to_notion_blocks(md_text)

    page = notion.pages.create(
        parent={"page_id": NOTION_PAGE_ID},
        properties={
            "title": [{
                "type": "text",
                "text": {"content": topic_title}
            }]
        }
    )

    page_id = page["id"]
    logger.info(f"Created Notion page for '{topic_title}' (Page ID: {page_id})")

    for i in range(0, len(blocks), batch_size):
        notion.blocks.children.append(
            block_id=page_id,
            children=blocks[i:i + batch_size]
        )

    logger.info(f"Uploaded {len(blocks)} blocks to Notion.")
    return page_id