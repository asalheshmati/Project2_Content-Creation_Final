# content_pipeline.py
# This file controls the full content creation flow.

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from knowledge_base import load_knowledge_base
from prompt_templates import create_content_prompt
from llm_integration import generate_ai_response

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PREVIEW_WIDTH = 1400
PREVIEW_MARGIN = 88
PREVIEW_BG = "#F7F7F7"
PREVIEW_CARD = "#FFFFFF"
PREVIEW_TEXT = "#0F172A"
PREVIEW_MUTED = "#475569"
PREVIEW_ACCENT = "#EC4899"
PREVIEW_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttf",
]


def safe_filename(value):
    return value.lower().replace(" ", "-").replace("/", "-")


def build_export_paths(output_folder, content_type):
    base_name = f"recru-ai-{safe_filename(content_type)}"
    return {
        "md": output_folder / f"{base_name}.md",
        "pdf": output_folder / f"{base_name}.pdf",
        "png": output_folder / f"{base_name}.png",
    }


def _load_font(size, bold=False):
    candidates = PREVIEW_FONT_CANDIDATES if bold else PREVIEW_FONT_CANDIDATES[::-1]
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def _wrap_text(text, font, max_width, draw):
    words = (text or "").split()
    if not words:
        return [""]

    lines = []
    current = words[0]
    for word in words[1:]:
        candidate = f"{current} {word}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    return lines


def _parse_preview_lines(content):
    items = []
    for raw_line in (content or "").splitlines():
        stripped = raw_line.strip()
        if not stripped:
            items.append(("spacer", ""))
            continue
        if stripped.startswith("# "):
            items.append(("title", stripped[2:].strip()))
        elif stripped.startswith("## "):
            items.append(("subtitle", stripped[3:].strip()))
        elif stripped.startswith("- "):
            items.append(("bullet", stripped[2:].strip()))
        else:
            items.append(("body", stripped))
    return items


def render_content_preview_png(content, title, output_path):
    """Render a clean preview image for text content."""
    width = PREVIEW_WIDTH
    card_width = width - PREVIEW_MARGIN * 2
    helper_img = Image.new("RGBA", (width, 200), PREVIEW_BG + "FF")
    draw = ImageDraw.Draw(helper_img)

    title_font = _load_font(44, bold=True)
    eyebrow_font = _load_font(18, bold=True)
    body_font = _load_font(26, bold=False)
    subtitle_font = _load_font(31, bold=True)
    bullet_font = body_font

    lines = []
    lines.append(("eyebrow", "RECRU AI"))
    lines.append(("headline", title))
    lines.append(("spacer", ""))

    for kind, text in _parse_preview_lines(content):
        if kind == "spacer":
            lines.append((kind, ""))
            continue
        lines.append((kind, text))

    measured = []
    content_height = PREVIEW_MARGIN * 2 + 130
    for kind, text in lines:
        if kind == "eyebrow":
            measured.append((kind, [text], eyebrow_font, 30, 14))
            content_height += 30
            continue
        if kind == "headline":
            wrapped = _wrap_text(text, title_font, int(card_width * 0.80), draw)
            measured.append((kind, wrapped, title_font, 56, 18))
            content_height += len(wrapped) * 58 + 18
            continue
        if kind == "title":
            wrapped = _wrap_text(text, subtitle_font, card_width, draw)
            measured.append((kind, wrapped, subtitle_font, 36, 12))
            content_height += len(wrapped) * 40 + 12
            continue
        if kind == "subtitle":
            wrapped = _wrap_text(text, subtitle_font, card_width, draw)
            measured.append((kind, wrapped, subtitle_font, 30, 10))
            content_height += len(wrapped) * 34 + 10
            continue
        if kind == "bullet":
            wrapped = _wrap_text(f"• {text}", bullet_font, card_width, draw)
            measured.append((kind, wrapped, bullet_font, 32, 10))
            content_height += len(wrapped) * 34 + 10
            continue
        wrapped = _wrap_text(text, body_font, card_width, draw)
        measured.append((kind, wrapped, body_font, 34, 10))
        content_height += len(wrapped) * 36 + 10

    height = max(1600, min(4200, content_height))
    image = Image.new("RGBA", (width, height), PREVIEW_BG + "FF")
    draw = ImageDraw.Draw(image)

    card_left = PREVIEW_MARGIN
    card_top = PREVIEW_MARGIN
    card_right = width - PREVIEW_MARGIN
    card_bottom = height - PREVIEW_MARGIN
    draw.rounded_rectangle(
        (card_left, card_top, card_right, card_bottom),
        radius=34,
        fill=PREVIEW_CARD + "FF",
        outline="#E2E8F0",
        width=2,
    )
    draw.rounded_rectangle(
        (card_left + 8, card_top + 8, card_right + 8, card_bottom + 8),
        radius=34,
        fill="#00000010",
    )

    x = card_left + 44
    y = card_top + 42

    for kind, wrapped, font, line_gap, post_gap in measured:
        if kind == "spacer":
            y += 22
            continue
        if kind == "eyebrow":
            draw.text((x, y), wrapped[0], font=font, fill=PREVIEW_ACCENT)
            y += line_gap
            continue
        if kind == "headline":
            for line in wrapped:
                draw.text((x, y), line, font=font, fill=PREVIEW_TEXT)
                bbox = draw.textbbox((x, y), line, font=font)
                y = bbox[3] + 8
            y += post_gap
            continue
        color = PREVIEW_TEXT
        for line in wrapped:
            draw.text((x, y), line, font=font, fill=color)
            bbox = draw.textbbox((x, y), line, font=font)
            y = bbox[3] + 8
        y += post_gap

    image.save(output_path)
    return output_path


def render_pdf_from_png(png_path, output_path):
    """Save the rendered preview image into a PDF with the same visual layout."""
    img = Image.open(png_path)
    page_width, page_height = letter
    margin = 36
    scale = min((page_width - margin * 2) / img.width, (page_height - margin * 2) / img.height)
    draw_width = img.width * scale
    draw_height = img.height * scale
    x = (page_width - draw_width) / 2
    y = (page_height - draw_height) / 2

    pdf = canvas.Canvas(str(output_path), pagesize=letter)
    pdf.drawImage(str(png_path), x, y, width=draw_width, height=draw_height, preserveAspectRatio=True, mask="auto")
    pdf.showPage()
    pdf.save()


def run_content_pipeline(
    content_type,
    topic,
    brand_mode="recru_ai",
    source_text="",
    visual_style="",
):
    """
    This function runs the full content pipeline.

    Steps:
    1. Load knowledge bases
    2. Create prompt
    3. Send prompt to AI
    4. Save output
    """

    if brand_mode == "white_label":
        primary_context = (
            "White-label B2B hiring platform. Use neutral language. Do not mention Recru AI."
        )
        secondary_context = source_text or "No external source provided."
    else:
        primary_context, secondary_context = load_knowledge_base()

    prompt = create_content_prompt(
        content_type=content_type,
        topic=topic,
        primary_context=primary_context,
        secondary_context=secondary_context,
        brand_mode=brand_mode,
        source_text=source_text,
        visual_style=visual_style,
    )

    generated_content = generate_ai_response(prompt)

    output_folder = PROJECT_ROOT / "outputs"
    output_folder.mkdir(exist_ok=True)

    output_files = build_export_paths(output_folder, content_type)

    output_files["md"].write_text(generated_content, encoding="utf-8")
    render_content_preview_png(generated_content, content_type, output_files["png"])
    render_pdf_from_png(output_files["png"], output_files["pdf"])

    return generated_content, output_files
