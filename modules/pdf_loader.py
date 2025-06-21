import fitz  # PyMuPDF

def clean_pdf_text(text):
    replacements = {
        "\u201c": '"', "\u201d": '"', "\u2018": "'",
        "\u2019": "'", "\u2013": '-', "\u2014": '-', "\xa0": ' '
    }
    for orig, repl in replacements.items():
        text = text.replace(orig, repl)
    return text

class PDFLoader:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages = self._load_pages()

    def _load_pages(self):
        try:
            doc = fitz.open(self.pdf_path)
            pages = [clean_pdf_text(doc[i].get_text()) for i in range(len(doc))]
            doc.close()
            return pages
        except Exception as e:
            print(f"PDF 로드 오류: {e}")
            return []
