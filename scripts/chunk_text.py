import sys, json

def chunk_text(pages, chunk_size=450, overlap=50):
    chunks = []
    current_text = ""
    current_pages = []

    for p in pages:
        paragraphs = p["text"].split('\n')
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_text) + len(para) < chunk_size:
                current_text += para + "\n"
                if p["page"] not in current_pages:
                    current_pages.append(p["page"])
            else:
                if current_text.strip():
                    chunks.append({
                        "text": current_text.strip(),
                        "pages": current_pages.copy(),
                        "index": len(chunks)
                    })
                current_text = para + "\n"
                current_pages = [p["page"]]

    if current_text.strip():
        chunks.append({
            "text": current_text.strip(),
            "pages": current_pages,
            "index": len(chunks)
        })

    return chunks

if __name__ == "__main__":
    data = json.loads(sys.argv[1])
    print(json.dumps(chunk_text(data), ensure_ascii=False))