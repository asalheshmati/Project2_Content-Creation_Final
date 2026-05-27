# Project Requirements

## 1. Project Summary

### Project Name
Recru AI – Hybrid AI Recruitment Content Generator

### Team Members
Asal Heshmati

### Problem We Are Solving
Recruitment for architecture and design firms is often slow, expensive, and manual.

Traditional recruitment agencies often charge high placement fees, and many small or mid-sized creative firms struggle to find qualified candidates quickly.

Recru AI solves this by combining:

- Human recruiter expertise
- AI-assisted sourcing
- Candidate screening
- Outreach support
- Recruitment workflow automation
- Brand-aligned content generation

This project focuses on building an AI content generation system for Recru AI using markdown knowledge bases and LLM prompting.

### Target User or Client
Primary users:

- Architecture firm founders
- Design studio owners
- Creative directors
- Hiring managers
- HR teams in architecture and design firms

### Success Criteria
The project is successful if:

- Markdown files are read successfully
- Both knowledge bases are used inside prompts
- The AI generates brand-aligned content
- The generated content feels specific to Recru AI
- The output is stronger than generic ChatGPT output
- Generated content can be saved in the outputs folder
- Uniqueness is demonstrated clearly

---

## 2. Scope

### Must Have

- [ ] Create project folder structure
- [ ] Create primary knowledge base
- [ ] Create secondary knowledge base
- [ ] Parse markdown files using Python
- [ ] Connect OpenAI API
- [ ] Generate content from prompt templates
- [ ] Save generated output
- [ ] Compare against generic ChatGPT output
- [ ] Maintain PROJECT_REQUIREMENTS.md
- [ ] Track prompts and changes

### Should Have

- [ ] Multiple content outputs: LinkedIn post, Instagram caption, blog outline, email newsletter
- [ ] Prompt template library
- [ ] Brand-specific content variations
- [ ] Human review step

### Could Have

- [ ] Monitoring trends pipeline
- [ ] Automated publishing workflow
- [ ] More advanced content formatting
- [ ] Vector database
- [ ] Full RAG pipeline

### Out of Scope for MVP

These are intentionally not included in the first version:

- Vector database
- Embeddings
- Full RAG system
- Advanced chatbot memory
- Automated social posting
- Full SaaS product
- Analytics dashboard

---

## 3. Functional Requirements

| ID | Requirement | Acceptance Criteria | Trello Card |
|---|---|---|---|
| FR-001 | App reads markdown files from primary knowledge base | Given markdown files, app loads brand content into Python | KB-1 |
| FR-002 | App reads markdown files from secondary knowledge base | Given markdown files, app loads market and audience context | KB-2 |
| FR-003 | App combines context into prompts | Prompt includes both knowledge bases | PR-1 |
| FR-004 | App connects to OpenAI API | AI model responds successfully | API-1 |
| FR-005 | App generates content brief | Brief is generated using the knowledge base context | BRIEF-1 |
| FR-006 | App generates final content | Output is created based on the brief and context | GEN-1 |
| FR-007 | App saves content to output folder | File is saved locally | OUT-1 |
| FR-008 | App demonstrates uniqueness | Comparison against generic ChatGPT is documented | UNI-1 |

---

## 4. Non-Functional Requirements

### Reliability
The script should run without errors when valid markdown files exist.

### Privacy and API-Key Handling
API keys must be stored inside `.env`.

`.env` must be excluded from GitHub using `.gitignore`.

No private client data should be included in the public repo.

### Maintainability
Code should be:

- Easy to read
- Simple for beginners to edit
- Split into clear Python files
- Commented clearly

### Usability
The project should be usable by a beginner with basic Python knowledge.

---

## 5. Kanban / Project Management

### Board Name
ACFT0520 – Project 2 – Team Recru AI

### Workflow Columns

- Backlog
- To Do
- In Progress
- Review
- Done

### WIP Limit
Maximum 2 tasks in progress at one time.

### Definition of Done
A task is done when:

- Code runs without errors
- Output has been reviewed manually
- The feature was tested successfully
- The work was committed to GitHub
- The Trello card was moved to Done

### Review Cadence

- Daily review during build
- Final review before submission

---

## 6. AI Coding-Agent Rules

### Which AI Coding Agents We Used

- ChatGPT
- VS Code AI assistant
- OpenAI API

### What the Agent Is Allowed To Do

- Generate starter code
- Help debug code
- Create prompt templates
- Help structure markdown files
- Help document the project

### What the Agent Is Not Allowed To Do

- Access API keys
- Store private data
- Push code directly without human review
- Make final decisions without review

### Human Review Process
All generated code is reviewed by the project owner before use.

Code is tested in the VS Code terminal before acceptance.

Prompt outputs are manually reviewed for:

- Brand alignment
- Clarity
- Quality
- Relevance
- Specificity

### Protecting Secrets and Private Data

- API keys are stored in `.env`
- `.env` is excluded from GitHub
- No private client-sensitive data is stored in the repo

---

## 7. Prompt Tracking Log

| Date | Tool / Agent | Prompt Goal | Prompt Summary | Output Used? | Human Review Notes | Related Commit |
|---|---|---|---|---|---|---|
| 2026-05-23 | ChatGPT | Project setup | Create folder structure and markdown knowledge base | Yes | Reviewed and edited | initial-setup |
| 2026-05-23 | ChatGPT | Brand voice | Generate Recru AI brand documents | Yes | Reviewed manually | kb-primary |
| 2026-05-23 | ChatGPT | Industry context | Generate market research markdown docs | Yes | Reviewed manually | kb-secondary |
| 2026-05-23 | ChatGPT | Python support | Generate markdown parsing starter code | Yes | To be tested locally | parser-v1 |
| 2026-05-23 | ChatGPT | Documentation | Create README and project requirements | Yes | Reviewed manually | docs-v1 |

---

## 8. Change Log

| Date | Requirement / Decision Changed | Why It Changed | Approved By |
|---|---|---|---|
| 2026-05-23 | Removed vector database from MVP | Not required for Project 2 core grading | Asal |
| 2026-05-23 | Chose markdown-based knowledge retrieval instead of full RAG | Faster and simpler beginner MVP | Asal |
| 2026-05-23 | Finalized Recru AI as project brand | Aligns with hybrid recruitment business concept | Asal |
| 2026-05-23 | Added uniqueness comparison deliverable | Required to prove output is not generic | Asal |

---

## 9. Instructor Explanation

If asked why this project does not include full RAG:

Vector stores and full RAG were optional stretch goals for this project.

For the MVP, I chose a lightweight file-based knowledge retrieval workflow. The system reads markdown files from the primary and secondary knowledge base folders, injects that context into the prompt, and generates brand-specific content using the LLM.

This meets the core project requirements while keeping the project scope manageable.
