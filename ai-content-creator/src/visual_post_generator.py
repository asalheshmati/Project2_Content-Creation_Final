"""Create branded social post images for Recru AI."""

import re
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

try:
    import cairosvg
except ModuleNotFoundError:  # pragma: no cover
    cairosvg = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = PROJECT_ROOT / "assets" / "recru-ai-logo.png"
OUTPUT_DIR = PROJECT_ROOT / "outputs"

INSTAGRAM_SIZE = (1080, 1080)
LINKEDIN_SIZE = (1200, 627)

PRESET_PALETTES = {
    "Recru Pink": {"background": "#F7D6E0", "text": "#111111"},
    "Soft Lavender": {"background": "#E7D8FF", "text": "#111111"},
    "Pale Blue": {"background": "#DDEBFF", "text": "#111111"},
    "Mint": {"background": "#DDF5EA", "text": "#111111"},
    "Cream": {"background": "#F8EEDC", "text": "#111111"},
    "Minimal White": {"background": "#F7F7F7", "text": "#111111"},
}

LOGO_BACKGROUND_COLORS = {
    "Soft Blush": "#F7D6E0",
    "Powder Pink": "#F9E3E8",
    "Cream": "#FFF7E8",
    "Warm Ivory": "#FAF3E0",
    "Sand": "#EDE3D3",
    "Champagne": "#F3E5D8",
    "Lavender Mist": "#E9E4F5",
    "Lilac": "#E8DDF3",
    "Powder Blue": "#DCEAF7",
    "Sky Mist": "#EAF4FC",
    "Sage": "#DDE8D8",
    "Mint": "#E6F3EA",
    "Peach": "#F9E2D2",
    "Butter": "#FFF3BF",
}

LOGO_BADGE_PRESETS = LOGO_BACKGROUND_COLORS

DEFAULT_LOGO_BACKGROUND_NAME = "Soft Blush"
DEFAULT_LOGO_BACKGROUND_HEX = LOGO_BACKGROUND_COLORS[DEFAULT_LOGO_BACKGROUND_NAME]
MIN_LOGO_CONTRAST = 4.5

SECONDARY_COLOR = "#FFFFFF"

FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "/System/Library/Fonts/Arial Bold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Supplemental/Helvetica.ttf",
]


def find_font(size, bold=False):
    """Load a readable system font, then fall back to Pillow's default font."""
    candidates = FONT_CANDIDATES if bold else FONT_CANDIDATES[::-1]
    for font_path in candidates:
        try:
            return ImageFont.truetype(font_path, size=size)
        except OSError:
            continue
    return ImageFont.load_default()


def wrap_text(text, font, max_width, draw):
    """Wrap text so it fits within the requested width."""
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


def _clean_text(text):
    text = re.sub(r"\n{3,}", "\n\n", (text or "").strip())
    text = re.sub(r"^\s*[-*•]\s*", "", text, flags=re.M)
    return text


def _split_sentences(text):
    cleaned = _clean_text(text)
    return [part.strip() for part in re.split(r"[\n\.!?]+", cleaned) if part.strip()]


def _limit_words(text, max_words):
    words = (text or "").split()
    if len(words) <= max_words:
        return text.strip()
    return " ".join(words[:max_words]).strip()


def _title_case_phrase(text):
    words = [part for part in re.split(r"\s+", (text or "").strip()) if part]
    if not words:
        return ""
    return " ".join(word.capitalize() for word in words)


def _topic_phrase(topic):
    cleaned = _clean_text(topic)
    return cleaned.strip().rstrip("?.!")


def _hex_to_rgb(value, fallback):
    text = (value or "").strip()
    if not text:
        return fallback
    if not text.startswith("#"):
        text = f"#{text}"
    if len(text) != 7:
        return fallback
    try:
        return tuple(int(text[index : index + 2], 16) for index in (1, 3, 5))
    except ValueError:
        return fallback


def _relative_luminance(rgb):
    def channel(value):
        value = value / 255.0
        return value / 12.92 if value <= 0.03928 else ((value + 0.055) / 1.055) ** 2.4

    r, g, b = rgb
    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def _contrast_ratio(rgb_a, rgb_b):
    lighter = max(_relative_luminance(rgb_a), _relative_luminance(rgb_b))
    darker = min(_relative_luminance(rgb_a), _relative_luminance(rgb_b))
    return (lighter + 0.05) / (darker + 0.05)


def _nearest_accessible_logo_background(target_rgb):
    """Choose the nearest pastel badge that keeps black text readable."""
    black = (17, 17, 17)
    accessible = []
    for name, hex_value in LOGO_BACKGROUND_COLORS.items():
        rgb = _hex_to_rgb(hex_value, (247, 214, 224))
        if _contrast_ratio(black, rgb) >= MIN_LOGO_CONTRAST:
            accessible.append((name, rgb))

    if not accessible:
        return DEFAULT_LOGO_BACKGROUND_HEX

    def distance(rgb):
        return sum((component - target) ** 2 for component, target in zip(rgb, target_rgb))

    _, chosen = min(accessible, key=lambda item: distance(item[1]))
    return "#%02X%02X%02X" % chosen


def resolve_logo_background_color(value=None):
    """Resolve a logo badge color to the safest pastel hex."""
    if not value:
        return DEFAULT_LOGO_BACKGROUND_HEX

    if value in LOGO_BACKGROUND_COLORS:
        return LOGO_BACKGROUND_COLORS[value]

    rgb = _hex_to_rgb(value, _hex_to_rgb(DEFAULT_LOGO_BACKGROUND_HEX, (247, 214, 224)))
    if _contrast_ratio((17, 17, 17), rgb) >= MIN_LOGO_CONTRAST:
        return "#%02X%02X%02X" % rgb
    return _nearest_accessible_logo_background(rgb)


def _blend_with_white(rgb, ratio=0.86):
    return tuple(int(component * ratio + 255 * (1 - ratio)) for component in rgb)


def resolve_palette(palette_name, custom_background=None, custom_text=None):
    """Return the background and text colors to use for a post."""
    preset = PRESET_PALETTES.get(palette_name, PRESET_PALETTES["Recru Pink"])
    background = _hex_to_rgb(custom_background, _hex_to_rgb(preset["background"], (247, 214, 224)))
    text = _hex_to_rgb(custom_text, _hex_to_rgb(preset["text"], (17, 17, 17)))
    return background, text


def resolve_background_color(background_color=None, custom_background=None):
    """Resolve a background hex string, preferring the custom override when present."""
    fallback = custom_background or background_color or "#F7D6E0"
    return _hex_to_rgb(fallback, (247, 214, 224))


def _remove_logo_background(logo):
    """Make the logo's pale background transparent so a badge color can show through."""
    if logo.mode != "RGBA":
        logo = logo.convert("RGBA")

    background = logo.getpixel((0, 0))[:3]
    pixels = logo.load()
    threshold = 46

    for y in range(logo.height):
        for x in range(logo.width):
            r, g, b, a = pixels[x, y]
            distance = abs(r - background[0]) + abs(g - background[1]) + abs(b - background[2])
            if distance <= threshold * 3:
                pixels[x, y] = (r, g, b, 0)
            else:
                pixels[x, y] = (r, g, b, 255)

    return logo


def _open_logo_image(source_path):
    """Open a logo image from PNG/JPG or rasterize SVG to RGBA."""
    suffix = source_path.suffix.lower()
    if suffix == ".svg":
        if cairosvg is None:
            raise RuntimeError(
                "SVG logo uploads require cairosvg. Install it with `pip install cairosvg`."
            )
        png_bytes = cairosvg.svg2png(url=str(source_path))
        return Image.open(BytesIO(png_bytes)).convert("RGBA")

    return Image.open(source_path).convert("RGBA")


def load_company_logo(company_logo_path=None, logo_size=170, logo_background_color="#F7D6E0"):
    """Load either an uploaded company logo or the default logo as a circular badge."""
    source_path = Path(company_logo_path) if company_logo_path else LOGO_PATH
    if not source_path.exists():
        source_path = LOGO_PATH
    if not source_path.exists():
        return None

    logo = _open_logo_image(source_path)
    logo = _remove_logo_background(logo)
    side = min(logo.size)
    left = (logo.width - side) // 2
    top = (logo.height - side) // 2
    logo = logo.crop((left, top, left + side, top + side))
    logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)

    badge_size = logo_size + max(18, int(logo_size * 0.12))
    badge = Image.new("RGBA", (badge_size, badge_size), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge)
    badge_rgb = _hex_to_rgb(resolve_logo_background_color(logo_background_color), _hex_to_rgb(DEFAULT_LOGO_BACKGROUND_HEX, (247, 214, 224)))
    badge_draw.ellipse((0, 0, badge_size - 1, badge_size - 1), fill=badge_rgb + (255,))

    offset = (badge_size - logo_size) // 2
    badge.paste(logo, (offset, offset), logo)

    return badge


def draw_logo(image, logo_size, logo_background_color="#F7D6E0", company_logo_path=None):
    """Draw the selected logo in the top-left corner with a colored badge."""
    badge = load_company_logo(company_logo_path=company_logo_path, logo_size=logo_size, logo_background_color=logo_background_color)
    if badge is None:
        return

    image.paste(badge, (54, 54), badge)


def _base_canvas(size, background_rgb):
    image = Image.new("RGBA", size, background_rgb + (255,))
    draw = ImageDraw.Draw(image)
    return image, draw


def _headline_layout(draw, text, start_size, max_width, max_lines=3, min_font_size=30):
    """Fit headline text by shrinking the font and wrapping conservatively."""
    size = start_size
    while size >= min_font_size:
        trial_font = find_font(size, bold=True)
        lines = wrap_text(text, trial_font, max_width, draw)
        if len(lines) <= max_lines:
            return trial_font, lines
        size -= 2
    final_font = find_font(min_font_size, bold=True)
    return final_font, wrap_text(text, final_font, max_width, draw)


def _subtitle_layout(draw, text, start_size, max_width, max_lines=2, min_font_size=20):
    size = start_size
    while size >= min_font_size:
        trial_font = find_font(size, bold=False)
        lines = wrap_text(text, trial_font, max_width, draw)
        if len(lines) <= max_lines:
            return trial_font, lines
        size -= 1
    final_font = find_font(min_font_size, bold=False)
    return final_font, wrap_text(text, final_font, max_width, draw)


def _template_copy(topic, caption, template_name):
    sentences = _split_sentences(caption)
    topic_text = (topic or "").strip()
    first_sentence = sentences[0] if sentences else ""
    topic_phrase = _topic_phrase(topic_text) or _topic_phrase(first_sentence)
    topic_title = _title_case_phrase(topic_phrase)
    topic_lower = topic_phrase.lower()

    if template_name == "Quote card":
        headline = f"{topic_title or 'Hiring'} deserves a calmer process"
        support = "Recru AI helps architecture and design firms hire with less noise."
    elif template_name == "Problem / solution":
        base = topic_title or "your studio"
        headline = f"Struggling to hire for {base}?"
        support = "Recru AI turns scattered hiring into a clearer process."
    else:
        if "architecture" in topic_lower or "design" in topic_lower:
            headline = "Hiring architects shouldn't feel like another full-time job."
        elif "recruit" in topic_lower or "hiring" in topic_lower:
            headline = f"{topic_title or 'Hiring'} made simpler."
        else:
            headline = f"{topic_title or 'Recruitment'} made simpler."
        support = "Recru AI helps teams hire with clarity and confidence."

    if not support:
        support = "AI-assisted recruitment for architecture and design firms."

    return headline, support


def _draw_template(
    image,
    draw,
    size,
    topic,
    caption,
    template_name,
    text_rgb,
    logo_background_color,
    company_logo_path=None,
):
    is_large = size[0] >= 1200
    headline_base = 62 if is_large else 56
    subtitle_base = 23 if is_large else 20

    headline, support = _template_copy(topic, caption, template_name)
    headline_width = int(size[0] * 0.66)
    support_width = int(size[0] * 0.54)

    logo_size = 200 if is_large else 170
    draw_logo(
        image,
        logo_size,
        logo_background_color=logo_background_color,
        company_logo_path=company_logo_path,
    )

    headline_font, headline_lines = _headline_layout(
        draw,
        headline,
        headline_base,
        headline_width,
        max_lines=3,
        min_font_size=34,
    )
    subtitle_font, support_lines = _subtitle_layout(
        draw,
        support,
        subtitle_base,
        support_width,
        max_lines=2,
        min_font_size=20,
    )

    x = 76 if is_large else 72
    y = 292 if is_large else 274

    for line in headline_lines[:3]:
        draw.text((x, y), line, font=headline_font, fill=text_rgb)
        bbox = draw.textbbox((x, y), line, font=headline_font)
        y = bbox[3] + (8 if is_large else 7)

    y += 14
    for line in support_lines[:2]:
        draw.text((x, y), line, font=subtitle_font, fill=text_rgb)
        bbox = draw.textbbox((x, y), line, font=subtitle_font)
        y = bbox[3] + 8


def _select_template(template_name, topic, caption):
    if template_name in {"Quote card", "Editorial announcement", "Problem / solution"}:
        return template_name

    text = f"{topic} {caption}".lower()
    if any(marker in text for marker in ('"', "“", "”", "quote")):
        return "Quote card"
    if "?" in text or any(marker in text for marker in ("struggling", "pain", "problem", "challenge", "hard to", "slow", "vacancy", "retain")):
        return "Problem / solution"
    return "Editorial announcement"


def _draw_social_post(
    size,
    topic,
    caption,
    output_path,
    background_color="#F7D6E0",
    text_color="#111111",
    template_name="Editorial announcement",
    logo_background_color="#F7D6E0",
    company_logo_path=None,
    custom_background=None,
):
    background_rgb = resolve_background_color(background_color, custom_background)
    text_rgb = _hex_to_rgb(text_color, (17, 17, 17))
    image, draw = _base_canvas(size, background_rgb)
    template = _select_template(template_name, topic, caption)
    _draw_template(
        image,
        draw,
        size,
        topic,
        caption,
        template,
        text_rgb,
        logo_background_color,
        company_logo_path,
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    image.save(output_path)
    return output_path


def create_instagram_post(
    topic,
    caption,
    output_path,
    background_color="#F7D6E0",
    text_color="#111111",
    company_logo_path=None,
    logo_background_color="#F7D6E0",
    template_name="Editorial announcement",
    custom_background=None,
):
    """Create a 1080x1080 Instagram-style post image."""
    return _draw_social_post(
        INSTAGRAM_SIZE,
        topic,
        caption,
        output_path,
        background_color,
        text_color,
        template_name,
        logo_background_color,
        company_logo_path,
        custom_background,
    )


def create_linkedin_post(
    topic,
    caption,
    output_path,
    background_color="#F7D6E0",
    text_color="#111111",
    company_logo_path=None,
    logo_background_color="#F7D6E0",
    template_name="Editorial announcement",
    custom_background=None,
):
    """Create a 1200x627 LinkedIn-style post image."""
    return _draw_social_post(
        LINKEDIN_SIZE,
        topic,
        caption,
        output_path,
        background_color,
        text_color,
        template_name,
        logo_background_color,
        company_logo_path,
        custom_background,
    )
