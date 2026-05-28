import sys, json

def generate_podcast_script(sources_text, focus="", duration="medium", style="casual", language="zh"):
    """
    Generate podcast script using LLM - this is a placeholder that returns structured prompt.
    The actual LLM call should be done by the Skill layer.
    """
    word_counts = {"short": 800, "medium": 2000, "long": 4000}
    words = word_counts.get(duration, 2000)

    return {
        "prompt": f"""Convert these research materials into a podcast dialogue between Alex (male) and Sam (female).

Parameters:
- Style: {style}
- Duration: {duration} (~{words} words)
- Focus: {focus or "all content"}
- Language: {language}

Requirements:
1. Opening 30s: self-intro + topic introduction
2. Body: discuss core ideas with specific data/quotes from sources
3. Natural speech elements: "um", "ah", "you know", laughter, surprise
4. Two hosts have disagreements, not one-sided explanation
5. Closing 30s: summary + "thanks for listening"
6. Total word count: ~{words}

Output format (STRICT):
Alex: [line]
Sam: [line]
Alex: [line]
...

Sources:
{sources_text}""",
        "target_words": words
    }

if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    result = generate_podcast_script(
        data.get("sources_text", ""),
        data.get("focus", ""),
        data.get("duration", "medium"),
        data.get("style", "casual"),
        data.get("language", "zh")
    )
    print(json.dumps(result, ensure_ascii=False))