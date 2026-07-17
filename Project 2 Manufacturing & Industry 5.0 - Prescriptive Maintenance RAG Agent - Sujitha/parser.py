import os
from dotenv import load_dotenv
load_dotenv()
PDF_FILE="data/raw/sample_manual.pdf"
OUTPUT_FILE="data/parsed/sample_manual.txt"

def parse_with_llamaparse(pdf_path):
    from llama_parse import LlamaParse
    parser=LlamaParse(api_key=os.getenv("LLAMA_CLOUD_API_KEY"),result_type="markdown")
    docs=parser.load_data(pdf_path)
    return "\n\n".join(doc.text for doc in docs)

def parse_with_pymupdf(pdf_path):
    import fitz

    doc = fitz.open(pdf_path)

    print("Total Pages:", len(doc))

    text = ""

    for page_num, page in enumerate(doc):
        page_text = page.get_text()
        print(f"Page {page_num + 1}: {len(page_text)} characters")
        text += page_text

    return text

if __name__=="__main__":
    try:
        text=parse_with_llamaparse(PDF_FILE)
    except Exception:
        text=parse_with_pymupdf(PDF_FILE)
    os.makedirs("data/parsed",exist_ok=True)
    with open(OUTPUT_FILE,"w",encoding="utf-8") as f:
        f.write(text)
    print("Saved:",OUTPUT_FILE)
