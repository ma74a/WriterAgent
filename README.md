# WriterAgent 🖊️

An AI-powered blog writing pipeline built with **LangGraph** and **Google Gemini**. Give it a topic, get back a fully structured, research-backed, illustrated technical blog post — complete with code examples, images, and clean Markdown/HTML output.

---

## How It Works

WriterAgent runs as a **parallel multi-node LangGraph pipeline**. Each node is a specialized agent with one job. Three of them run in parallel after planning, then a final assembler stitches everything together.

```mermaid
graph TD
    A([🧑 User Prompt]) --> B[🔍 Prompt Analyzer]
    B --> C[🌐 Web Searcher]
    C --> D[📋 Blog Planner]

    D --> E[✍️ Content Generator]
    D --> F[💻 Code Generator]
    D --> G[🖼️ Image Handler]

    E --> H[🧩 Blog Assembler]
    F --> H
    G --> H

    H --> I([📄 Markdown + HTML Output])

    style A fill:#1e1e2e,color:#cdd6f4,stroke:#89b4fa
    style I fill:#1e1e2e,color:#cdd6f4,stroke:#a6e3a1
    style B fill:#313244,color:#cdd6f4,stroke:#89dceb
    style C fill:#313244,color:#cdd6f4,stroke:#89dceb
    style D fill:#313244,color:#cdd6f4,stroke:#f38ba8
    style E fill:#313244,color:#cdd6f4,stroke:#a6e3a1
    style F fill:#313244,color:#cdd6f4,stroke:#a6e3a1
    style G fill:#313244,color:#cdd6f4,stroke:#a6e3a1
    style H fill:#313244,color:#cdd6f4,stroke:#fab387
```

---

## Pipeline Nodes

| Node | Role |
|---|---|
| **Prompt Analyzer** | Extracts topic, audience, tone, word count, and whether code/images are needed |
| **Web Searcher** | Runs targeted Tavily searches to ground the blog in real, current information |
| **Blog Planner** | Produces a structured blueprint — title, sections, intro, conclusion — for downstream agents |
| **Content Generator** | Writes each section in full using the plan and research as context |
| **Code Generator** | Produces runnable code examples with dependencies for sections that need them |
| **Image Handler** | Searches and downloads royalty-free images from Openverse for relevant sections |
| **Blog Assembler** | Combines all outputs into clean, structured Markdown with proper attribution |

---

## Output

Given a prompt like:

> *Write a technical but beginner-friendly blog post explaining how to build a YOLO project using Python. Include practical code examples, explain the architecture, and include diagrams where useful. Approximately 2000 words.*

WriterAgent produces:

- `output/blog.md` — structured Markdown with headings, code blocks, and image embeds
- `output/blog.html` — rendered HTML, ready to publish
- `output/images/` — downloaded section images with full attribution metadata

---

## Project Structure

```
WriterAgent/
├── app/
│   ├── graph.py          # LangGraph pipeline definition
│   ├── state.py          # BlogState TypedDict
│   ├── schemas.py        # Pydantic models for structured LLM output
│   ├── llm.py            # Gemini model setup
│   ├── web_search.py     # Tavily search client
│   ├── image_search.py   # Openverse image search + download
│   ├── output.py         # Markdown and HTML file writers
│   └── nodes/
│       ├── analyzer.py   # Prompt Analyzer node
│       ├── researcher.py # Web Searcher node
│       ├── planner.py    # Blog Planner node
│       ├── content.py    # Content Generator node
│       ├── code.py       # Code Generator node
│       ├── images.py     # Image Handler node
│       └── assembler.py  # Blog Assembler node
├── output_graphs/        # LangGraph pipeline visualizations
├── notebooks/            # Exploration and prototyping notebooks
├── main.py               # Entry point
└── requirements.txt
```

---

## Quickstart

### 1. Clone and install

```bash
git clone https://github.com/ma74a/WriterAgent.git
cd WriterAgent
pip install -r requirements.txt
```

### 2. Set environment variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key
TAVILY_API_KEY=your_tavily_api_key
```

| Key | Where to get it |
|---|---|
| `GOOGLE_API_KEY` | [Google AI Studio](https://aistudio.google.com/app/apikey) |
| `TAVILY_API_KEY` | [Tavily](https://tavily.com) |

### 3. Write your prompt and run

Edit the `user_prompt` in `main.py`, then:

```bash
python main.py
```

Output files appear in `output/`.

---

## Tech Stack

| Component | Technology |
|---|---|
| Agent orchestration | [LangGraph](https://github.com/langchain-ai/langgraph) |
| LLM | Google Gemini via `langchain-google-genai` |
| Web research | [Tavily](https://tavily.com) |
| Image search | [Openverse](https://openverse.org) |
| Structured output | Pydantic + `with_structured_output` |
| HTML rendering | Python `markdown` library |

---

## Graph Visualizations

Several pipeline variants are saved in `output_graphs/`:

| Graph | Description |
|---|---|
| `graph_sequentially.png` | Linear version — one node at a time |
| `graph_parallelly_without_assembler.png` | Parallel content/code/image, no assembler |
| `graph_parallelly_with_assembler.png` | Full parallel pipeline with assembler |
| `graph_parallelly_with_assembler_and_web_searcher.png` | Complete pipeline including web search |

---

## License

MIT