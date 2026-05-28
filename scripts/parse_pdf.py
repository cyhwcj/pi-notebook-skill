import sys, json, pdfplumber

def parse_pdf(file_path):
    pages = []
    with pdfplumber.open(file_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():
                pages.append({"page": i+1, "text": text.strip()})
    return pages

if __name__ == "__main__":
    print(json.dumps(parse_pdf(sys.argv[1]), ensure_ascii=False))