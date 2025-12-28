import os
import re
import logging
import google.generativeai as genai
from config import GEMINI_API_KEY

# === CONFIG ===
genai.configure(api_key=GEMINI_API_KEY)

# === LOGGER ===
logger = logging.getLogger(__name__)

# === CHUNKING ===
def chunk_text(text, max_chars=12000):
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current = ""

    for s in sentences:
        if len(current) + len(s) <= max_chars:
            current += s + " "
        else:
            chunks.append(current.strip())
            current = s + " "

    if current.strip():
        chunks.append(current.strip())

    return chunks

# === 1. Merge all transcripts ===
def merge_transcripts(transcript_folder):
    files = sorted(
        f for f in os.listdir(transcript_folder) if f.endswith(".txt")
    )

    merged_text = ""
    for file in files:
        with open(os.path.join(transcript_folder, file), "r", encoding="utf-8") as f:
            merged_text += f.read().strip() + "\n\n"

    return merged_text.strip()


# === 2. Summarize using Gemini (chunk-aware) ===
def summarize_notes_gemini(raw_text, topic_title):
    chunks = chunk_text(raw_text)

    logger.info(f"Transcript split into {len(chunks)} chunk(s)")
    
    model = genai.GenerativeModel("models/gemini-flash-latest")

    outputs = []

    for idx, chunk in enumerate(chunks, start=1):
        logger.info(f"Processing chunk {idx}/{len(chunks)}")
        prompt = f"""
You are reorganizing a lecture transcript into structured study notes for Notion.

This is a continuation of the same lecture. 
Do NOT restate conclusions, summaries, or section endings from earlier parts unless they appear in the transcript below.

### Rules
- Preserve all information present in the transcript
- Do not add new facts, interpretations, or examples
- Do not remove minor or side points
- Rephrase only when needed for clarity
- If the transcript restates previously introduced ideas for emphasis or recap, merge those statements into the original relevant section instead of creating a new section or repeating the idea. Do not duplicate headings or bullet points for recap content.
- When numbering is required, include the number as part of the text itself. Do not rely on Markdown numbered lists 

### Structure
- Use Markdown headings up to H3 only (#, ##, ###)
- Use headings only for true section boundaries
- When listing defined qualities, roles, responsibilities, principles, or classifications, use numbered lists (1., 2., 3.) instead of bullet points.
- Use bullet points for lists of ideas
- Avoid nested paragraphs inside bullet points
- Do not use horizontal rules
- Ensure the output maps cleanly to Notion blocks
- Each concept, definition, or list should appear only once in the final notes, regardless of how many times it appears in the transcript. All later mentions must be integrated into the first occurrence.

### Context
Lecture topic: {topic_title}
Transcript content below is part {idx} of {len(chunks)}.

### Transcript
{chunk}
-Assume the transcript is a continuous spoken stream. Identify conceptual boundaries based on meaning, not formatting, and group accordingly.

Return only the reorganized notes in clean, Notion-compatible Markdown.
"""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.0,
                "max_output_tokens": 16000
            }
        )

        outputs.append(response.text.strip())

    # Join chunks with spacing to avoid heading collisions
    return "\n\n".join(outputs)


# === 3. Save summarized notes ===
def save_summarized_notes(topic_title, notes_text, notes_folder):
    os.makedirs(notes_folder, exist_ok=True)

    safe_title = topic_title.replace(" ", "_")
    path = os.path.join(notes_folder, f"{safe_title}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(notes_text)

    logger.info(f"Summarized notes saved → {path}")
    
    return path


# === 4. Full pipeline ===
def process_topic_summarization(topic_title, transcripts_folder, notes_folder, logger):
    raw_text = merge_transcripts(transcripts_folder)
    logger.info("Starting Gemini summarization pipeline")
   
    summarized_notes = summarize_notes_gemini(raw_text, topic_title)
    save_summarized_notes(topic_title, summarized_notes, notes_folder)