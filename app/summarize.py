import os
import google.generativeai as genai
from config import GEMINI_API_KEY

# === CONFIG ===
genai.configure(api_key=GEMINI_API_KEY)


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

# === 2. Summarize using Gemini ===
def summarize_notes_gemini(raw_text, topic_title):
    prompt = f"""
You are reorganizing a lecture transcript into structured study notes.

Rules (very important):
- Preserve ALL information from the transcript
- Do NOT add new facts, explanations, or examples
- Do NOT remove minor points
- Do NOT aggressively compress content
- Rephrase only when needed for clarity, not brevity

Structural rules (STRICT — follow exactly):
- Use Markdown headings up to H3 only (## and ###). Do NOT use H4 or deeper.
- Do NOT simulate headings using bold text.
- Use headings only for true section boundaries.
- Use bullet points for lists of ideas.
- Keep bullet points concise and single-purpose.
- Avoid nested paragraphs inside bullet points.
- Avoid horizontal rules (---).
- Ensure the structure maps cleanly to Notion blocks.

Your task is NOT to summarize,
but to reorganize the content into:
- Clear sections (Headings should be limited to H1, H2 and H3 only)
- Bullet points
- Short, readable paragraphs where appropriate

Lecture topic: {topic_title}

Transcript:
{raw_text}

Return the reorganized notes only, in clean Notion-compatible Markdown.

"""

    model = genai.GenerativeModel("models/gemini-flash-latest")

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": 0.0,
            "max_output_tokens": 10000000
        }
    )

    return response.text.strip()

# === 3. Save summarized notes ===
def save_summarized_notes(topic_title, notes_text, notes_folder):
    os.makedirs(notes_folder, exist_ok=True)

    safe_title = topic_title.replace(" ", "_")
    path = os.path.join(notes_folder, f"{safe_title}.md")

    with open(path, "w", encoding="utf-8") as f:
        f.write(notes_text)

    print(f"Summarized notes saved → {path}")
    return path

# === 4. Full pipeline ===
def process_topic_summarization(topic_title, transcripts_folder, notes_folder):
    raw_text = merge_transcripts(transcripts_folder)
    print("Summarizing notes with Gemini...")
    summarized_notes = summarize_notes_gemini(raw_text, topic_title)
    save_summarized_notes(topic_title, summarized_notes, notes_folder)

# === Example usage ===
if __name__ == "__main__":
    topic_title = "Example"
    process_topic_summarization(topic_title)
