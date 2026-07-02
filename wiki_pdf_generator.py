import os
import json
import urllib.request
import urllib.parse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "Document_Corpus",
)
os.makedirs(OUTPUT_DIR, exist_ok=True)


def save_to_pdf(filename, title, article_text):
    """Generates a formatted PDF file from a text string."""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 15))

    body_style = styles["Normal"]
    paragraphs = article_text.split("\n\n")

    for p_text in paragraphs:
        p_text = p_text.strip()
        if p_text and not p_text.startswith("=="):
            clean_text = (
                p_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            )
            story.append(Paragraph(clean_text, body_style))
            story.append(Spacer(1, 10))

    doc.build(story)


def fetch_and_make_pdfs(topics):
    """Scrapes Wikipedia and saves each article as a separate PDF."""
    for topic in topics:
        print(f"Fetching '{topic}' from Wikipedia...")
        url_topic = urllib.parse.quote(topic)
        url = f"https://en.wikipedia.org/w/api.php?action=query&format=json&prop=extracts&titles={url_topic}&explaintext=1&redirects=1"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode("utf-8"))

            pages = data["query"]["pages"]
            page_id = list(pages.keys())[0]

            if page_id == "-1":
                print(f"[-] Topic '{topic}' not found on Wikipedia.")
                continue

            text = pages[page_id]["extract"]

            safe_filename = "".join(
                c for c in topic if c.isalnum() or c in (" ", "_", "-")
            ).strip()
            pdf_filename = os.path.join(OUTPUT_DIR, f"{safe_filename}.pdf")

            save_to_pdf(pdf_filename, topic, text)
            print(f"[+] Successfully saved: {pdf_filename}")

        except Exception as e:
            print(f"[-] Error fetching/creating PDF for '{topic}': {e}")


topics_list = [
    "Narendra Modi",
    "Indian Prime Minister",
    "Bharatiya Janata Party",
    "Varanasi",
]

fetch_and_make_pdfs(topics_list)
print(f"\n Done! Check your '{OUTPUT_DIR}' directory.")
