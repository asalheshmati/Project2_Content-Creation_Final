# prompt_templates.py
# This file stores reusable prompt templates.

def create_content_prompt(
    content_type,
    topic,
    primary_context,
    secondary_context,
    brand_mode="recru_ai",
    source_text="",
    visual_style="",
):
    """
    This function creates the full prompt we send to the AI.

    content_type = LinkedIn Post, LinkedIn Card, Instagram Card, Instagram Caption, Blog Post, or Email Newsletter.
    topic = what the user wants the content to be about.
    """

    brand_instruction = (
        "This is a white-label company using the platform. Do not mention Recru AI. "
        "Use the uploaded company logo in visual content. Write in a neutral B2B hiring voice."
        if brand_mode == "white_label"
        else "This is Recru AI content. Use Recru AI positioning, tone, default logo, and the primary and secondary brand knowledge folders."
    )

    source_instruction = (
        "Use the provided source content as the main factual base. Stay accurate to it. Do not invent claims, data, names, or results."
        if source_text.strip()
        else "Use the topic, user prompt, and available brand knowledge base as the main source."
    )

    output_requirements = {
        "LinkedIn Card": "Format the output as a concise card/carousel concept with strong headline hierarchy.",
        "Instagram Card": "Format the output as a concise square-card concept with strong visual headline hierarchy.",
        "Blog Post": "Format the output as a blog post or detailed blog outline with sections and subheads.",
        "Email Newsletter": "Format the output as a newsletter with subject line, intro, body, and CTA.",
        "LinkedIn Post": "Format the output as a polished written LinkedIn post that reads naturally on the platform.",
        "Instagram Caption": "Format the output as a polished written Instagram caption that reads naturally on the platform.",
    }.get(content_type, "Format the output clearly for the selected content type.")

    source_section = f"\nSource text:\n{source_text.strip()}\n" if source_text.strip() else ""

    prompt = f"""
You are an AI content assistant for Recru AI.

Brand instruction:
{brand_instruction}

Source instruction:
{source_instruction}

Use the brand knowledge below:
{primary_context}

Use the market and audience research below:
{secondary_context}

Task:
Create a {content_type} about this topic:
{topic}

Visual style:
{visual_style or "Not applicable"}

{source_section}Output format requirements:
{output_requirements}

Rules:
- Keep the language simple and practical
- Avoid generic AI language
- Include a clear hiring pain point when relevant
- Make the content specific to the provided source and/or brand context
- End with a simple call to action
"""

    return prompt
