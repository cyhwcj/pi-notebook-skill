# NotebookLM Agent - Architecture Document (arch.md)

> **Version**: v1.0.0  
> **Date**: 2026-05-28  
> **Related PRD**: prd.md  

---

## 1. Architecture Principles

1. **Zero Intrusion**: Do not modify pi-web core code, only extend through Skill system
2. **Fully Local**: All data, models, vector stores stored locally, no cloud services (except LLM API)
3. **Progressive Enhancement**: Core must work, Podcast and Studio can be toggled independently
4. **Bash Orchestration**: Heavy logic via bash calling Python scripts, Skill layer only handles prompt orchestration

---

## 2. System Architecture

### 2.1 Layered Architecture

```
+-------------------------------------------------------------+
|  Presentation Layer (pi-web Next.js)                        |
|  +----------+ +----------+ +----------+ +----------+        |
|  | Chat     | | Explorer | | Skills   | | Models   |        |
|  | Panel    | | Panel    | | Panel    | | Panel    |        |
|  +-----+----+ +-----+----+ +-----+----+ +-----+----+        |
|        +------------+-----------+------------+               |
|                      |                                       |
|                Agent Loop                                    |
|           (read / write / edit / bash)                     |
+----------------------+--------------------------------------+
                       |
+----------------------+--------------------------------------+
|  Skill Layer         |                                       |
|  +-------------------+-------------------------------+     |
|  | notebooklm-core   |  Source Mgmt / RAG / Citations|     |
|  | notebooklm-podcast|  Podcast (depends core+edge-tts)|    |
|  | notebooklm-studio |  Mindmap/Flashcards/Report     |     |
|  +-------------------+-------------------------------+     |
+----------------------+--------------------------------------+
                       |
+----------------------+--------------------------------------+
|  Script Layer (Python)|                                      |
|  +----------+ +--------+ +----------+ +----------+         |
|  | parse_   | | chunk_ | | embed_   | | search_  |         |
|  | pdf.py   | | text.py| | store.py | | query.py |         |
|  +----------+ +--------+ +----------+ +----------+         |
|  +----------+ +--------+ +----------+                     |
|  | generate | | merge_ | | export_  |                     |
|  | podcast  | | audio  | | format   |                     |
|  | _script  | | .py    | | .py      |                     |
|  | .py      | |        | |          |                     |
|  +----------+ +--------+ +----------+                     |
+-------------------------------------------------------------+
                       |
+----------------------+--------------------------------------+
|  Data Layer          |                                       |
|  +----------+ +--------+ +----------+ +----------+         |
|  | notebooks| |sources/| | chunks/  | | chroma_  |         |
|  | .json    | |        | |          | | db/      |         |
|  +----------+ +--------+ +----------+ +----------+         |
|  +----------+                                              |
|  | exports/ |  Podcast/Mindmap/Flashcards/Report          |
|  +----------+                                              |
+-------------------------------------------------------------+
```

### 2.2 Data Flow

```
User uploads PDF
  -> pi-web Chat receives file path
  -> notebooklm-core SKILL.md triggered
  -> bash: python parse_pdf.py
    -> pdfplumber extracts text + page numbers
    -> Returns JSON: [{"page": 1, "text": "..."}, ...]
  -> bash: python chunk_text.py
    -> 450 chars per chunk, 50 chars overlap
    -> Returns chunks: [{"text": "...", "pages": [1,2], "index": 0}, ...]
  -> bash: python embed_store.py
    -> sentence-transformers generates 384-dim embedding
    -> ChromaDB collection.add()
  -> Update notebooks.json
  -> Return to user: "Added, X pages Y chunks"

User asks question
  -> pi-web Chat receives query
  -> notebooklm-core SKILL.md triggered
  -> bash: python search_query.py "question"
    -> sentence-transformers encodes query
    -> ChromaDB collection.query(n_results=5)
    -> Filter similarity < 0.3
    -> Return top chunks
  -> Build context prompt
  -> LLM generates answer (with citations)
  -> Extract citation tags
  -> Return to user + save chat history

User says "generate podcast"
  -> notebooklm-podcast SKILL.md triggered
  -> Read current Notebook Sources (via core)
  -> LLM generates podcast script (Alex/Sam dialogue)
  -> bash: python parse_dialogue.py
  -> bash: uvx edge-tts (per role)
  -> bash: python merge_audio.py (ffmpeg)
  -> Save to exports/
  -> Return download link
```

---

## 3. Module Design

### 3.1 Module Dependency Graph

```
notebooklm-core
    |-- pdf skill (existing)
    |-- chromadb (pip)
    |-- sentence-transformers (pip)

notebooklm-podcast
    |-- notebooklm-core
    |-- edge-tts skill (existing)
    |-- ffmpeg (system)

notebooklm-studio
    |-- notebooklm-core
    |-- LLM (pi-ai unified interface)
```

### 3.2 Core Classes/Functions (Python Script Layer)

```python
# parse_pdf.py
"""Parse PDF, extract text with page numbers"""
def parse_pdf(file_path: str) -> list[dict]:
    """
    Returns: [{"page": int, "text": str}, ...]
    """

# chunk_text.py
"""Text chunking"""
def chunk_text(
    pages: list[dict], 
    chunk_size: int = 450, 
    overlap: int = 50
) -> list[dict]:
    """
    Returns: [{"text": str, "pages": list[int], "index": int}, ...]
    """

# embed_store.py
"""Generate embeddings and store to ChromaDB"""
def embed_and_store(
    notebook_id: str,
    source_id: str,
    filename: str,
    chunks: list[dict]
) -> None:
    """Use all-MiniLM-L6-v2 to generate embeddings, store in ChromaDB"""

def search_chunks(
    notebook_id: str,
    query: str,
    top_k: int = 5,
    threshold: float = 0.3
) -> list[dict]:
    """
    Returns: [{"text": str, "metadata": dict, "distance": float}, ...]
    """

# notebook_manager.py
"""Notebook CRUD"""
def create_notebook(name: str) -> str:
def get_notebook(notebook_id: str) -> dict:
def delete_notebook(notebook_id: str) -> None:
def add_source(notebook_id: str, file_path: str) -> dict:
def list_sources(notebook_id: str) -> list[dict]:

# podcast_generator.py
"""Podcast generation"""
def generate_script(
    sources: list[dict],
    focus: str = "",
    duration: str = "medium",
    style: str = "casual",
    language: str = "zh"
) -> str:
    """Return Alex/Sam dialogue format script"""

def parse_script(script: str) -> list[dict]:
    """Parse into [{"speaker": "Alex", "text": "..."}, ...]"""

def generate_audio(dialogue: list[dict], output_path: str) -> str:
    """Call edge-tts + ffmpeg, return MP3 path"""

# studio_tools.py
"""Studio toolset"""
def generate_mindmap(sources: list[dict]) -> str:
    """Return Mermaid code"""

def generate_flashcards(sources: list[dict], count: int = 10) -> str:
    """Return Markdown Q&A"""

def generate_report(sources: list[dict], style: str = "academic") -> str:
    """Return Markdown report"""

def generate_timeline(sources: list[dict]) -> str:
    """Return Markdown table"""
```

---

## 4. Data Model

### 4.1 ER Diagram

```
+-------------+       +-------------+       +-------------+
|  Notebook   |<----->|   Source    |<----->|   Chunk     |
+-------------+  1:N  +-------------+  1:N  +-------------+
| id (PK)     |       | id (PK)     |       | id (PK)     |
| name        |       | notebook_id |       | source_id   |
| created_at  |       | filename    |       | text        |
| sources[]   |       | title       |       | embedding   |
| chat_history|       | type        |       | pages[]     |
+-------------+       | page_count  |       | chunk_index |
                      | chunk_count |       +-------------+
                      | added_at    |
                      +-------------+
                            |
                            v
                      +-------------+
                      |  Citation   |
                      +-------------+
                      | message_id  |
                      | source_id   |
                      | page        |
                      | chunk_index |
                      +-------------+
```

### 4.2 Entity Definitions

#### Notebook
```json
{
  "id": "nb_{timestamp}",
  "name": "string",
  "created_at": "ISO8601",
  "sources": ["src_id1", "src_id2"],
  "chat_history": [
    {
      "role": "user|assistant",
      "content": "string",
      "citations": [
        {"source_id": "src_001", "page": 3, "chunk_index": 2}
      ],
      "timestamp": "ISO8601"
    }
  ],
  "settings": {
    "context_mode": "auto|summary|full|none",
    "default_model": "deepseek-chat"
  }
}
```

#### Source
```json
{
  "id": "src_{timestamp}",
  "notebook_id": "nb_001",
  "filename": "paper.pdf",
  "title": "Attention Is All You Need",
  "type": "pdf|txt|url",
  "page_count": 8,
  "chunk_count": 12,
  "added_at": "ISO8601",
  "file_size": 1024000,
  "checksum": "md5_hash"
}
```

#### Chunk (ChromaDB)
```json
{
  "id": "src_001_chunk_0",
  "document": "chunk text content",
  "embedding": [0.1, 0.2, ...],
  "metadata": {
    "source_id": "src_001",
    "filename": "paper.pdf",
    "pages": "[1,2]",
    "chunk_index": 0
  }
}
```

---

## 5. Interface Design

### 5.1 Skill Tool Interface (Exposed to Agent)

| Tool Name | Skill | Parameters | Return | Description |
|-----------|-------|------------|--------|-------------|
| `add_source` | core | `file_path`, `notebook_id?` | source object | Upload and parse |
| `remove_source` | core | `source_id` | bool | Delete Source |
| `list_sources` | core | `notebook_id?` | source[] | List Sources |
| `grounded_chat` | core | `query`, `context_mode?` | answer + citations | RAG Q&A |
| `create_notebook` | core | `name` | notebook object | Create |
| `delete_notebook` | core | `notebook_id` | bool | Delete |
| `switch_notebook` | core | `notebook_id` | bool | Switch |
| `generate_podcast` | podcast | `focus?`, `duration?`, `style?` | MP3 path + script | Podcast |
| `generate_mindmap` | studio | `notebook_id?` | Mermaid code | Mindmap |
| `generate_flashcards` | studio | `count?`, `notebook_id?` | Markdown | Flashcards |
| `generate_report` | studio | `style?`, `notebook_id?` | Markdown | Report |
| `generate_timeline` | studio | `notebook_id?` | Markdown | Timeline |

### 5.2 Python Script CLI Interface

All scripts called via `bash`, parameters via command line, results via stdout JSON:

```bash
# Parse PDF
python scripts/parse_pdf.py "path/to/file.pdf"
# Returns: [{"page": 1, "text": "..."}, ...]

# Chunk
python scripts/chunk_text.py --input json_string --size 450 --overlap 50
# Returns: [{"text": "...", "pages": [1], "index": 0}, ...]

# Embed and store
python scripts/embed_store.py --notebook nb_001 --source src_001 --chunks json_string
# Returns: {"status": "ok", "chunks_stored": 12}

# Search
python scripts/search_query.py --notebook nb_001 --query "transformer architecture" --top_k 5
# Returns: [{"text": "...", "metadata": {...}, "distance": 0.15}, ...]

# Notebook CRUD
python scripts/notebook_manager.py --action create --name "Deep Learning"
# Returns: {"id": "nb_001", "name": "Deep Learning", ...}
```

---

## 6. Technology Selection

| Component | Choice | Reason |
|-----------|--------|--------|
| Agent Framework | pi-web (@agegr/pi-web) | User already installed, Skill system available |
| LLM Interface | pi-ai (DeepSeek V4 Flash) | Already configured, no changes needed |
| Embedding | sentence-transformers (all-MiniLM-L6-v2) | Local, free, 384-dim sufficient |
| Vector DB | ChromaDB (PersistentClient) | Local file storage, zero config |
| PDF Parsing | pdfplumber | Preserves layout, accurate page numbers |
| HTML Parsing | BeautifulSoup4 + requests | Standard solution |
| TTS | edge-tts (uvx) | Existing skill, free, multilingual |
| Audio Merge | ffmpeg | System standard tool |
| Data Format | JSON | Simple, readable, easy to debug |
| Config Management | Env vars + notebooks.json | No complex config system needed |

---

## 7. Deployment Architecture

```
Windows 10+ (User Machine)
|-- pi-web (Next.js, port 30141)
|   |-- Agent Loop
|   |-- Skill Loader
|-- Python 3.10+
|   |-- chromadb
|   |-- sentence-transformers
|   |-- pdfplumber
|   |-- beautifulsoup4
|-- ChromaDB (Local SQLite)
|   |-- ~/pi-cwd-20260526/notebooklm_data/chroma_db/
|-- ffmpeg (System PATH)
```

---

## 8. Security Design

1. **API Key Isolation**: Reuse pi-web existing model config, no additional storage
2. **Path Safety**: All file operations restricted to `~/pi-cwd-20260526/notebooklm_data/`
3. **Command Injection Prevention**: Python scripts use parameterized input, no shell command concatenation
4. **Data Privacy**: All data stored locally, no cloud upload (except LLM API calls)

---

## 9. Extensibility Design

1. **New Source Types**: Add `parse_youtube.py` next to `parse_pdf.py`, add type check in Skill
2. **New Studio Tools**: Add new tool definitions in `notebooklm-studio`, reuse core search capability
3. **New Podcast Styles**: Modify prompt templates, no code changes needed
4. **Multilingual Support**: edge-tts already supports multiple languages, just specify language param in prompt

---

## 10. Iteration Record

| Date | Version | Change | Reason |
|------|---------|--------|--------|
| 2026-05-28 | v1.0.0 | Initial version | 1-day MVP requirement finalized |

---

> **Architect Note**: This architecture follows "simplicity first" principle. All complex logic sinks to Python scripts, Skill layer only handles prompt orchestration and tool calls. No unnecessary abstractions, guaranteed 1-day delivery.
