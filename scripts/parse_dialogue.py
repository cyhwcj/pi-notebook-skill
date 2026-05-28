import sys, json, re

def parse_dialogue(script_text):
    """Parse podcast script into dialogue lines."""
    lines = []
    pattern = r'^(Alex|Sam):\s*(.+)$'
    for line in script_text.strip().split('\n'):
        match = re.match(pattern, line.strip())
        if match:
            lines.append({
                "speaker": match.group(1),
                "text": match.group(2).strip()
            })
    return lines

if __name__ == "__main__":
    script = sys.argv[1] if len(sys.argv) > 1 else sys.stdin.read()
    result = parse_dialogue(script)
    print(json.dumps(result, ensure_ascii=False))