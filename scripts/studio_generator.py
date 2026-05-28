import sys, json

def generate_mindmap(sources_text):
    """Generate mindmap prompt - actual generation done by LLM."""
    return {
        "prompt": f"""Convert these materials into a hierarchical mindmap.
Return STRICT Mermaid syntax:

```mermaid
mindmap
  root((Core Topic))
    Branch1
      Sub1.1
      Sub1.2
    Branch2
      Sub2.1
```

Requirements:
- Max 3 levels
- 2-6 chars per node
- Cover 80%+ core concepts
- Only output Mermaid code, no explanations

Materials:
{sources_text}"""
    }

def generate_flashcards(sources_text, count=10):
    """Generate flashcards prompt - actual generation done by LLM."""
    return {
        "prompt": f"""Generate {count} flashcards from these materials.

Format (STRICT):
---
Q: [question]
A: [answer, max 50 chars]
Source: [filename, page]
Difficulty: [easy/medium/hard]
---

Requirements:
- Cover core concepts, definitions, key data
- Questions must be transformed, not copied from source
- Answers must have basis in sources
- Include difficulty rating

Materials:
{sources_text}"""
    }

def generate_report(sources_text, style="academic"):
    """Generate report prompt - actual generation done by LLM."""
    return {
        "prompt": f"""Generate a {style} report from these materials.

Structure:
# Title
## Abstract (200 words)
## Introduction
## Body (with subsections)
## Conclusion
## References

Requirements:
- All claims must cite sources (filename, page)
- Do not fabricate data
- Word count: 1500-2000

Materials:
{sources_text}"""
    }

def generate_timeline(sources_text):
    """Generate timeline prompt - actual generation done by LLM."""
    return {
        "prompt": f"""Extract time-related events from these materials, sort chronologically.

Format:
| Time | Event | Source |
|------|-------|--------|
| 2020-01 | event description | source.pdf page |

If no clear time, mark as "Time unclear".

Materials:
{sources_text}"""
    }

if __name__ == "__main__":
    action = sys.argv[1]
    sources_text = sys.argv[2] if len(sys.argv) > 2 else ""

    if action == "mindmap":
        result = generate_mindmap(sources_text)
    elif action == "flashcards":
        count = int(sys.argv[3]) if len(sys.argv) > 3 else 10
        result = generate_flashcards(sources_text, count)
    elif action == "report":
        style = sys.argv[3] if len(sys.argv) > 3 else "academic"
        result = generate_report(sources_text, style)
    elif action == "timeline":
        result = generate_timeline(sources_text)
    else:
        result = {"error": "Unknown action"}

    print(json.dumps(result, ensure_ascii=False))