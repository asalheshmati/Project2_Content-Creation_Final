"""Gradio frontend for the Recru AI content generator."""

from pathlib import Path

try:
    import gradio as gr
except ModuleNotFoundError as exc:
    print(
        "Error: Gradio is not installed. Run `pip install -r requirements.txt` "
        "from the ai-content-creator folder, then launch `python src/main.py` again."
    )
    raise SystemExit(1) from exc

from content_pipeline import run_content_pipeline
from llm_integration import validate_openai_configuration
from visual_post_generator import LOGO_BACKGROUND_COLORS, create_instagram_post, create_linkedin_post, resolve_logo_background_color
from source_ingestion import build_source_text
from content_pipeline import render_pdf_from_png


PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = PROJECT_ROOT / "assets" / "recru-ai-logo.png"

CONTENT_TYPES = [
    "LinkedIn Post",
    "LinkedIn Card",
    "Instagram Card",
    "Instagram Caption",
    "Blog Post",
    "Email Newsletter",
]

VISUAL_STYLES = [
    "Editorial announcement",
    "Quote card",
    "Problem / solution",
]

BACKGROUND_COLORS = {
    "Recru Pink": "#F7D6E0",
    "Soft Lavender": "#E7D8FF",
    "Pale Blue": "#DDEBFF",
    "Mint Green": "#DDF5EA",
    "Warm Cream": "#F8EEDC",
    "Minimal White": "#F7F7F7",
    "Custom": "#F7D6E0",
}

BACKGROUND_OPTIONS = list(BACKGROUND_COLORS.keys())
LOGO_BACKGROUND_OPTIONS = [
    (f"{name} — {hex_value}", hex_value)
    for name, hex_value in LOGO_BACKGROUND_COLORS.items()
]

EXAMPLES = [
    ["LinkedIn Post", "new hiring initiative"],
    ["LinkedIn Card", "design studio hiring"],
    ["Instagram Card", "brand announcement"],
    ["Instagram Caption", "candidate shortlist tips"],
    ["Blog Post", "architecture recruitment trends"],
    ["Email Newsletter", "design firm founder hiring pain points"],
]


def render_background_preview(background_color, custom_background):
    """Show the selected background as a small preview swatch."""
    selected = custom_background.strip() if background_color == "Custom" and custom_background else BACKGROUND_COLORS.get(background_color, "#F7D6E0")
    return f"""
    <div class="bg-preview">
        <div class="bg-preview-swatch" style="background: {selected};"></div>
        <div class="bg-preview-meta">
            <div class="bg-preview-label">Current background</div>
            <div class="bg-preview-value">{selected.upper()}</div>
        </div>
    </div>
    """


def generate_content(content_type, topic, brand_mode="recru_ai", source_text="", visual_style=""):
    """Run the content pipeline and return UI-friendly outputs."""
    topic = (topic or "").strip()
    if not topic and not source_text.strip():
        raise gr.Error("Please enter a topic before generating content.")

    try:
        generated_content, output_files = run_content_pipeline(
            content_type,
            topic,
            brand_mode=brand_mode,
            source_text=source_text,
            visual_style=visual_style,
        )
    except RuntimeError as exc:
        raise gr.Error(str(exc)) from exc

    return (
        generated_content,
        str(output_files["md"]),
        str(output_files["pdf"]),
        str(output_files["png"]),
    )


def generate_social_visual(
    content_type,
    topic,
    caption_text,
    visual_style,
    background_color,
    logo_background_color,
    company_logo_path,
    custom_background,
):
    """Create a branded PNG for supported social post types."""
    if content_type not in ("LinkedIn Card", "Instagram Card"):
        return None

    visual_folder = PROJECT_ROOT / "outputs"
    visual_folder.mkdir(exist_ok=True)
    safe_name = content_type.lower().replace(" ", "-")
    visual_path = visual_folder / f"recru-ai-{safe_name}.png"

    selected_background = custom_background.strip() if background_color == "Custom" and custom_background else BACKGROUND_COLORS.get(background_color, "#F7D6E0")
    selected_logo_background = resolve_logo_background_color(logo_background_color)

    if content_type == "LinkedIn Card":
        create_linkedin_post(
            topic,
            caption_text,
            visual_path,
            background_color=selected_background,
            text_color="#111111",
            company_logo_path=company_logo_path,
            logo_background_color=selected_logo_background,
            template_name=visual_style,
        )
    else:
        create_instagram_post(
            topic,
            caption_text,
            visual_path,
            background_color=selected_background,
            text_color="#111111",
            company_logo_path=company_logo_path,
            logo_background_color=selected_logo_background,
            template_name=visual_style,
        )

    return str(visual_path)


def generate_all(
    content_type,
    topic,
    generate_visual,
    visual_style,
    background_color,
    logo_background_color,
    company_logo_path,
    custom_background,
    article_url,
    uploaded_pdf,
):
    """Generate text, exports, and optional branded visual."""
    brand_mode = "white_label" if company_logo_path else "recru_ai"
    try:
        source_text = build_source_text(article_url, uploaded_pdf)
    except Exception as exc:
        raise gr.Error(f"Could not extract the provided source content: {exc}") from exc

    generated_content, md_path, pdf_path, preview_png = generate_content(
        content_type,
        topic,
        brand_mode=brand_mode,
        source_text=source_text,
        visual_style=visual_style,
    )

    if generate_visual or content_type in ("LinkedIn Card", "Instagram Card"):
        visual_image = generate_social_visual(
            content_type,
            topic,
            generated_content,
            visual_style,
            background_color,
            logo_background_color,
            company_logo_path,
            custom_background,
        )
        if visual_image:
            preview_png = visual_image
            render_pdf_from_png(visual_image, pdf_path)

    return (
        generated_content,
        md_path,
        preview_png,
        gr.update(value=pdf_path, interactive=True),
        gr.update(value=preview_png, interactive=True),
    )


def build_app():
    """Create the Gradio interface."""
    with gr.Blocks() as demo:
        with gr.Column(elem_classes=["shell"]):
            gr.HTML(
                """
                <div class="app-header">
                    <div class="app-title">Recru AI Content Studio</div>
                    <div class="app-tagline">
                        Create polished hiring content for LinkedIn, Instagram, blogs, newsletters, and branded visual posts.
                    </div>
                    <div class="app-subtext">
                        Choose a format, add your topic or source, then generate reusable content in seconds.
                    </div>
                </div>
                """
            )

        with gr.Row():
            with gr.Column(scale=1, elem_classes=["card"]):
                content_type = gr.Radio(
                    choices=CONTENT_TYPES,
                    value=CONTENT_TYPES[0],
                    label="Content type",
                    elem_id="content-type-pills",
                )

                with gr.Tabs():
                    with gr.Tab("Manual Prompt"):
                        gr.HTML(
                            """
                            <div class="tab-intro">
                                <div class="tab-intro-title">Manual Prompt</div>
                                <div class="tab-intro-subtitle">Start from scratch with a topic and your selected content type.</div>
                            </div>
                            """
                        )
                        topic = gr.Textbox(
                            label="Topic",
                            placeholder="e.g. recruitment for architecture industry",
                            lines=2,
                        )
                        gr.Markdown("Use a topic and the Recru AI brand knowledge to create content from scratch.")
                        gr.Examples(
                            examples=EXAMPLES,
                            inputs=[content_type, topic],
                            label="Try an example",
                        )
                    with gr.Tab("Create from Source"):
                        gr.HTML(
                            """
                            <div class="tab-intro tab-intro-source">
                                <div class="tab-intro-title">Create from Source</div>
                                <div class="tab-intro-subtitle">Turn an article, PDF, or white-label logo into on-brand content.</div>
                            </div>
                            """
                        )
                        gr.Markdown("Use an article link, PDF, or uploaded logo to create source-based content.")
                        article_url = gr.Textbox(
                            label="Article link",
                            placeholder="Paste article URL here",
                        )
                        uploaded_pdf = gr.File(
                            label="Upload PDF",
                            file_types=[".pdf"],
                            type="filepath",
                        )
                        gr.Markdown("Optional: upload your company logo to customize the generated post.")
                        company_logo_path = gr.File(
                            label="Upload company logo",
                            file_types=[".png", ".jpg", ".jpeg", ".svg"],
                            type="filepath",
                        )
                        gr.Markdown("Uploading a logo switches the generator to white-label mode.")

                generate_visual = gr.Checkbox(
                    label="Generate Visual Post",
                    value=True,
                )
                visual_style = gr.Dropdown(
                    choices=VISUAL_STYLES,
                    value="Editorial announcement",
                    label="Visual style",
                )
                background_color = gr.Dropdown(
                    choices=BACKGROUND_OPTIONS,
                    value="Recru Pink",
                    label="Background color",
                )
                gr.Markdown("Choose a background color for your generated social post.")
                custom_background = gr.Textbox(
                    label="Custom background hex",
                    placeholder="#F7D6E0",
                )
                background_preview = gr.HTML(
                    render_background_preview("Recru Pink", ""),
                    elem_id="background-preview",
                )
                logo_background_color = gr.Dropdown(
                    choices=LOGO_BACKGROUND_OPTIONS,
                    value="#F7D6E0",
                    label="Logo background color",
                    elem_id="logo-background-select",
                )
                generate_btn = gr.Button(
                    "Generate Content",
                    variant="primary",
                    elem_id="generate-btn",
                )

            with gr.Column(scale=1, elem_classes=["card"]):
                output_pdf = gr.DownloadButton(
                    label="Download PDF",
                    value=None,
                    variant="secondary",
                    interactive=False,
                    elem_id="download-pdf-btn",
                )
                output_png = gr.DownloadButton(
                    label="Download PNG",
                    value=None,
                    variant="secondary",
                    interactive=False,
                    elem_id="download-png-btn",
                )
                output_preview = gr.Image(
                    label="Generated preview",
                    interactive=False,
                    type="filepath",
                )
                output_content = gr.Markdown(
                    label="Generated content",
                    elem_id="output-content",
                )
                output_md = gr.File(label="Saved Markdown")

        with gr.Accordion("What this app does", open=False):
            gr.Markdown(
                """
                - Reads Recru AI brand and market knowledge from the markdown library.
                - Builds a prompt around your selected content format and topic.
                - Sends the prompt to OpenAI and saves the result in `outputs/`.
                """
            )

        generate_btn.click(
            fn=generate_all,
            inputs=[
                content_type,
                topic,
                generate_visual,
                visual_style,
                background_color,
                logo_background_color,
                company_logo_path,
                custom_background,
                article_url,
                uploaded_pdf,
            ],
            outputs=[output_content, output_md, output_preview, output_pdf, output_png],
        )

        background_color.change(
            fn=render_background_preview,
            inputs=[background_color, custom_background],
            outputs=[background_preview],
        )

        custom_background.change(
            fn=render_background_preview,
            inputs=[background_color, custom_background],
            outputs=[background_preview],
        )

    return demo


if __name__ == "__main__":
    validate_openai_configuration()
    app = build_app()
    app.launch(
        inbrowser=True,
        theme=gr.themes.Soft(),
        css="""
        .shell {
            max-width: 1720px;
            margin: 0 auto;
            padding: 14px 16px 28px;
            color: #ffffff;
        }
        body {
            background:
                radial-gradient(circle at top left, rgba(123, 77, 255, 0.16), transparent 32%),
                linear-gradient(180deg, #55575f 0%, #494b52 100%);
        }
        .gradio-container,
        .gradio-container * {
            box-sizing: border-box;
        }
        .logo-wrap {
            display: none;
        }
        .app-header {
            margin-bottom: 32px;
            padding: 24px 0 12px;
        }
        .app-title {
            color: #ffffff;
            font-size: 42px;
            font-weight: 800;
            letter-spacing: -0.04em;
            margin-bottom: 10px;
            line-height: 1.08;
        }
        .app-tagline {
            color: rgba(255, 255, 255, 0.88);
            font-size: 20px;
            font-weight: 500;
            max-width: 780px;
            line-height: 1.4;
            margin-bottom: 8px;
        }
        .app-subtext {
            color: rgba(255, 255, 255, 0.55);
            font-size: 16px;
            line-height: 1.5;
            max-width: 720px;
        }
        .hero {
            display: none;
        }
        .card [role="tab"] {
            color: #ffffff !important;
            background: rgba(255,255,255,0.10) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            border-radius: 999px !important;
            box-shadow: none !important;
            font-weight: 700 !important;
        }
        .card [role="tab"][aria-selected="true"] {
            background: #5b4dff !important;
            color: #ffffff !important;
            border-color: #5b4dff !important;
        }
        .card [role="tab"] * {
            color: inherit !important;
        }
        .tab-intro {
            margin: 2px 0 16px;
            padding: 14px 16px;
            border-radius: 16px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
        }
        .tab-intro-source {
            background: rgba(255,255,255,0.08);
        }
        .tab-intro-title {
            font-size: 1rem;
            font-weight: 800;
            color: #ffffff;
            margin-bottom: 4px;
        }
        .tab-intro-subtitle {
            font-size: 0.95rem;
            line-height: 1.45;
            color: rgba(255,255,255,0.75);
        }
        #content-type-pills {
            margin-bottom: 14px;
        }
        #content-type-pills label {
            display: inline-flex;
            align-items: center;
            margin: 0 10px 10px 0;
            padding: 10px 14px;
            border-radius: 999px;
            border: 1px solid rgba(255,255,255,0.12);
            background: rgba(255,255,255,0.08);
            color: #ffffff;
            font-weight: 600;
            transition: all 0.18s ease;
            cursor: pointer;
            gap: 8px;
        }
        #content-type-pills label:hover {
            border-color: rgba(109,93,252,0.45);
            box-shadow: 0 8px 18px rgba(15, 23, 42, 0.10);
        }
        #content-type-pills label:has(input[type="radio"]:checked) {
            background: #5b4dff;
            border-color: #5b4dff;
            box-shadow: 0 12px 24px rgba(91, 77, 255, 0.24);
            color: #ffffff;
        }
        #content-type-pills label:has(input[type="radio"]:checked) * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        #content-type-pills input[type="radio"] {
            margin-right: 0;
            accent-color: #ec4899;
        }
        .bg-preview {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 8px 0 16px;
            padding: 12px 14px;
            border-radius: 16px;
            background: rgba(255,255,255,0.08);
            border: 1px solid rgba(255,255,255,0.12);
        }
        .bg-preview-swatch {
            width: 44px;
            height: 44px;
            border-radius: 999px;
            border: 1px solid rgba(17,17,17,0.12);
            box-shadow: inset 0 0 0 3px rgba(255,255,255,0.72);
            flex: 0 0 auto;
        }
        .bg-preview-meta {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .bg-preview-label {
            font-size: 0.88rem;
            color: rgba(255,255,255,0.72);
        }
        .bg-preview-value {
            font-size: 0.94rem;
            font-weight: 700;
            color: #ffffff;
            letter-spacing: 0.02em;
        }
        .logo-background {
            border-radius: 12px;
        }
        .logo-text {
            color: #111111;
            fill: #111111;
        }
        .card {
            background: rgba(67,69,76,0.90);
            border: 1px solid rgba(255,255,255,0.16);
            border-radius: 18px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.22);
            color: #ffffff;
            padding: 16px;
        }
        .card,
        .card *,
        .tab-intro,
        .tab-intro *,
        .bg-preview,
        .bg-preview *,
        #content-type-pills,
        #content-type-pills *,
        .gr-accordion,
        .gr-accordion * {
            color: #ffffff;
        }
        #output-content {
            background: rgba(255,255,255,0.96);
            color: #0f172a !important;
            padding: 16px 18px;
            border-radius: 16px;
            border: 1px solid rgba(148,163,184,0.18);
            line-height: 1.75;
        }
        #output-content * {
            color: #0f172a !important;
        }
        .card h3, .card h4, .card p, .card span, .card label {
            color: #ffffff;
        }
        .card .gr-markdown h3, .card .gr-markdown h4 {
            color: #ffffff;
            margin-bottom: 0.35rem;
        }
        .card .gr-markdown p {
            color: rgba(255,255,255,0.78);
            margin-top: 0;
            line-height: 1.7;
            font-size: 0.99rem;
        }
        .card .gr-textbox label,
        .card .gr-dropdown label,
        .card .gr-file label,
        .card .gr-radio label,
        .card .gr-checkbox label,
        .card .gr-number label,
        .card .gr-slider label,
        .card .gr-button,
        .card .gr-markdown,
        .card .gr-html {
            color: #ffffff;
        }
        .card input,
        .card textarea,
        .card select {
            color: #0f172a !important;
            background: #ffffff !important;
            border-color: rgba(148,163,184,0.28) !important;
            line-height: 1.6;
        }
        .card [data-testid="dropdown"],
        .card [data-testid="dropdown"] button,
        .card [role="combobox"],
        .card [aria-haspopup="listbox"],
        .card .wrap .secondary[role="button"] {
            background: #ffffff !important;
            color: #0f172a !important;
            border-color: rgba(148,163,184,0.24) !important;
        }
        .card [data-testid="dropdown"] *,
        .card [role="combobox"] *,
        .card [aria-haspopup="listbox"] *,
        .card [aria-haspopup="listbox"] svg {
            color: #0f172a !important;
            fill: #0f172a !important;
        }
        .card [role="listbox"],
        .card ul[role="listbox"] {
            background: #2f3a4a !important;
            border-color: rgba(255,255,255,0.12) !important;
        }
        .card [role="option"] {
            color: #ffffff !important;
            background: #2f3a4a !important;
        }
        .card [role="option"][aria-selected="true"],
        .card [role="option"]:hover {
            background: #5b4dff !important;
            color: #ffffff !important;
        }
        .card [role="option"][aria-selected="true"] *,
        .card [role="option"]:hover * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        .card [role="tab"],
        .card button[role="tab"] {
            color: #0f172a !important;
            background: rgba(248,250,252,0.96) !important;
            border: 1px solid rgba(148,163,184,0.2) !important;
            border-radius: 999px !important;
            box-shadow: none !important;
            font-weight: 700 !important;
        }
        .card [role="tab"][aria-selected="true"],
        .card button[role="tab"][aria-selected="true"] {
            background: #0f172a !important;
            color: #ffffff !important;
            border-color: #0f172a !important;
        }
        .card [role="tab"] *,
        .card button[role="tab"] * {
            color: inherit !important;
        }
        .card input::placeholder,
        .card textarea::placeholder {
            color: #64748b !important;
        }
        .card .wrap,
        .card .wrap * {
            color: #ffffff;
        }
        .card .wrap .secondary,
        .card .wrap .description,
        .card .wrap .helper {
            color: rgba(255,255,255,0.72) !important;
        }
        .card .prose,
        .card .prose * {
            color: #ffffff;
        }
        .card .prose p {
            color: rgba(255,255,255,0.78);
        }
        .card .svelte-1ipelgc,
        .card .svelte-1ipelgc * {
            color: #ffffff;
        }
        #logo-background-select [data-testid="dropdown"],
        #logo-background-select [role="combobox"],
        #logo-background-select button {
            background: #2f3a4a !important;
            color: #ffffff !important;
            border-color: rgba(255,255,255,0.12) !important;
        }
        #logo-background-select [data-testid="dropdown"] *,
        #logo-background-select [role="combobox"] *,
        #logo-background-select button *,
        #logo-background-select svg {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        #logo-background-select [role="listbox"],
        #logo-background-select ul[role="listbox"] {
            background: #2f3a4a !important;
            border-color: rgba(255,255,255,0.12) !important;
        }
        #logo-background-select [role="option"] {
            color: #ffffff !important;
            background: #2f3a4a !important;
        }
        #logo-background-select [role="option"][aria-selected="true"],
        #logo-background-select [role="option"]:hover {
            background: #5b4dff !important;
            color: #ffffff !important;
        }
        #logo-background-select [role="option"][aria-selected="true"] *,
        #logo-background-select [role="option"]:hover * {
            color: #ffffff !important;
            fill: #ffffff !important;
        }
        #generate-btn button {
            background: linear-gradient(135deg, #6d5dfc 0%, #5b4dff 100%) !important;
            border: none !important;
            color: white !important;
            box-shadow: 0 14px 28px rgba(91, 77, 255, 0.30) !important;
        }
        #generate-btn button:hover {
            background: linear-gradient(135deg, #7f72ff 0%, #6d5dfc 100%) !important;
            box-shadow: 0 16px 32px rgba(91, 77, 255, 0.38) !important;
            transform: translateY(-1px);
        }
        #generate-btn button:active {
            transform: translateY(0px);
            box-shadow: 0 10px 20px rgba(91, 77, 255, 0.22) !important;
        }
        #download-pdf-btn button,
        #download-png-btn button {
            width: 100% !important;
            min-height: 76px !important;
            border-radius: 18px !important;
            font-size: 1.2rem !important;
            font-weight: 700 !important;
            border: none !important;
            color: white !important;
            background: linear-gradient(135deg, #6d5dfc 0%, #5b4dff 100%) !important;
            box-shadow: 0 14px 28px rgba(91, 77, 255, 0.30) !important;
        }
        #download-pdf-btn button:hover,
        #download-png-btn button:hover {
            background: linear-gradient(135deg, #7f72ff 0%, #6d5dfc 100%) !important;
        }
        #download-pdf-btn,
        #download-png-btn {
            width: 100%;
            margin-bottom: 14px;
        }
        .gr-dataframe,
        .gr-dataset {
            color: #ffffff;
        }
        .gr-dataframe table,
        .gr-dataset table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 14px;
            overflow: hidden;
        }
        .gr-dataframe th,
        .gr-dataset th {
            background: rgba(255,255,255,0.96) !important;
            color: #0f172a !important;
            font-weight: 700 !important;
            padding: 14px 16px !important;
            border: 1px solid rgba(255,255,255,0.16) !important;
        }
        .gr-dataframe td,
        .gr-dataset td {
            background: rgba(63,64,70,0.96) !important;
            color: #ffffff !important;
            padding: 14px 16px !important;
            border: 1px solid rgba(255,255,255,0.10) !important;
        }
        @media (max-width: 900px) {
            .card {
                padding: 14px;
            }
            #content-type-pills label {
                width: 100%;
                margin-right: 0;
            }
            #download-pdf-btn button,
            #download-png-btn button {
                min-height: 64px !important;
                font-size: 1rem !important;
            }
        }
        """,
    )
