# knowledge_base.py
# This file loads the primary and secondary knowledge bases.

from pathlib import Path

from document_processor import read_markdown_folder

PROJECT_ROOT = Path(__file__).resolve().parents[1]
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"


def load_knowledge_base():
    """
    This function loads both knowledge base folders.

    Primary knowledge base = Recru AI brand/company information.
    Secondary knowledge base = market, trends, competitors, and pain points.
    """

    primary_context = read_markdown_folder(KNOWLEDGE_BASE_DIR / "primary")
    secondary_context = read_markdown_folder(KNOWLEDGE_BASE_DIR / "secondary")

    return primary_context, secondary_context
