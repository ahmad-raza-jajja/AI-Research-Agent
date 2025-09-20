import streamlit as st
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import json

# =========================
# 🖨️ SIMPLE DEBUG LOGGER
# =========================
def log_debug(message):
    """Print a clean debug message to console."""
    print(f"[DEBUG] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

# =========================
# 🎨 LOAD CUSTOM CSS
# =========================
def load_css(css_file_path):
    """Load custom CSS file into Streamlit app."""
    try:
        with open(css_file_path, "r", encoding="utf-8") as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
            log_debug(f"✅ Loaded CSS file: {css_file_path} ({len(css_content.splitlines())} lines)")
    except FileNotFoundError:
        log_debug(f"⚠️ CSS file not found: {css_file_path}")
        st.warning(f"⚠️ CSS file not found: {css_file_path}")

# =========================
# 💾 SAVE REPORT TO PDF
# =========================
def save_report_to_pdf(query, summary, sources, username):
    """Generate a PDF report of the research results."""
    reports_dir = "reports"
    os.makedirs(reports_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_path = os.path.join(reports_dir, f"{username}_{timestamp}.pdf")

    doc = SimpleDocTemplate(file_path, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<b>Research Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Topic:</b> {query}", styles["Heading2"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Summary:</b> {summary}", styles["BodyText"]))
    elements.append(Spacer(1, 12))

    if sources:
        elements.append(Paragraph("<b>Sources:</b>", styles["Heading3"]))
        for s in sources:
            elements.append(Paragraph(f"- {s['title']} ({s['link']})", styles["BodyText"]))
            elements.append(Spacer(1, 6))

    doc.build(elements)

    log_debug(f"📄 PDF report generated: {file_path}")
    save_user_history(username, query, file_path)
    return file_path

# =========================
# 🧾 SAVE + LOAD HISTORY
# =========================
def save_user_history(username, query, file_path):
    """Save user's research history to a JSON file."""
    history_file = "user_history.json"
    history = []

    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            try:
                history = json.load(f)
            except json.JSONDecodeError:
                history = []

    history.append({
        "user": username,
        "title": query,
        "path": file_path,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M")
    })

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=4)

    log_debug(f"💾 History updated for user: {username} | Total reports: {len(history)}")

def load_user_history(username):
    """Load saved research reports for a specific user."""
    history_file = "user_history.json"
    if os.path.exists(history_file):
        with open(history_file, "r", encoding="utf-8") as f:
            try:
                all_history = json.load(f)
                user_history = [h for h in all_history if h["user"] == username]
                log_debug(f"📂 Loaded {len(user_history)} reports for user: {username}")
                return user_history
            except json.JSONDecodeError:
                log_debug(f"⚠️ Failed to load history file (corrupted JSON)")
                return []
    log_debug(f"ℹ️ No history found for user: {username}")
    return []
