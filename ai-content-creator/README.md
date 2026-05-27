# Recru AI – Hybrid AI Recruitment Content Generator

## Project Overview

This project is a beginner-friendly AI content generation app.

It reads markdown documents from two knowledge bases:

- A primary knowledge base with Recru AI brand information
- A secondary knowledge base with recruitment market context

Then it sends that information to an AI model and generates content that sounds specific to Recru AI.

## What the App Does

The app can:

- Read `.md` files
- Load brand voice and audience documents
- Load market trends and competitor documents
- Create a content brief
- Generate final content
- Save the result in the `outputs/` folder as Markdown and PDF
- Generate branded LinkedIn and Instagram visual posts as PNGs
- Preview the branded PNG inside the Gradio app
- Help compare Recru AI content against generic ChatGPT output
- Launch a Gradio web UI for a smoother content-generation workflow

## Tech Stack

- Python
- Markdown
- OpenAI API
- python-dotenv
- Gradio
- ReportLab
- Pillow
- VS Code
- GitHub

## Folder Structure

```text
ai-content-creator/
│
├── src/
│   ├── document_processor.py
│   ├── knowledge_base.py
│   ├── prompt_templates.py
│   ├── llm_integration.py
│   ├── visual_post_generator.py
│   ├── content_pipeline.py
│   └── main.py
│
├── knowledge_base/
│   ├── primary/
│   │   ├── brand_voice.md
│   │   ├── audience.md
│   │   ├── services.md
│   │   └── past_content.md
│   │
│   └── secondary/
│       ├── market_trends.md
│       ├── competitor_analysis.md
│       ├── audience_pain_points.md
│       └── industry_news.md
│
├── prompts/
│   ├── linkedin_prompt.md
│   ├── instagram_prompt.md
│   ├── blog_prompt.md
│   └── email_prompt.md
│
├── outputs/
├── config/
├── screenshots/
├── PROJECT_REQUIREMENTS.md
├── README.md
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup Instructions

### 1. Open the project folder in VS Code

Open the folder called:

```bash
ai-content-creator
```

### 2. Create a virtual environment

A virtual environment is a private Python workspace for this project.

Run:

```bash
python3 -m venv venv
```

### 3. Activate the virtual environment

On Mac:

```bash
source venv/bin/activate
```

### 4. Install packages

Packages are extra Python tools your project needs.

Run:

```bash
pip install -r requirements.txt
```

### 5. Create your `.env` file

Copy `.env.example`.

Rename the copy to:

```text
.env
```

Add your OpenAI API key:

```text
OPENAI_API_KEY=your_api_key_here
```

Do not upload `.env` to GitHub.

### 6. Run the app

Run:

```bash
python src/main.py
```

This launches the Gradio UI in your browser.

## Example Use

The app asks what content you want to create.

Examples:

- LinkedIn Post
- LinkedIn Card
- Instagram Card
- Instagram Caption
- Blog Post
- Email Newsletter

You can also switch to the `Create from Source` tab to paste an article link, upload a PDF, and white-label the visual output with your own company logo.

Then it creates and saves the output.

## Uniqueness Strategy

This project avoids generic AI output by using:

- Recru AI brand voice
- Architecture and design recruitment context
- Audience pain points
- Market trends
- Competitor positioning
- Human review

## Final Deliverables

- GitHub repo
- Working Python app
- Knowledge base markdown files
- Prompt templates
- Generated content output
- Uniqueness comparison
- README.md
- PROJECT_REQUIREMENTS.md
- Trello screenshots
