import fitz  # PyMuPDF
import re

class PDFLoader:
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.pages = []
        self.load_pdf()
    
    def clean_text(self, text: str) -> str:
        text = re.sub(r'\n+', '\n', text)
        text = re.sub(r' +', ' ', text)
        text = text.replace('\x00', '').replace('\ufeff', '')
        return text.strip()
    
    def load_pdf(self):
        try:
            doc = fitz.open(self.pdf_path)
            print(f"PDF 문서 열기 성공: {len(doc)} 페이지")
            
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                
                if text and len(text.strip()) > 50:
                    cleaned_text = self.clean_text(text)
                    if cleaned_text:
                        self.pages.append(cleaned_text)
                        print(f"페이지 {page_num + 1} 로드됨: {len(cleaned_text)}자")
                
            doc.close()
            print(f"총 {len(self.pages)}개 유효 페이지 로드됨")
            
            # 디버깅용 (샘플 확인)
            if self.pages:
                print(f"첫 번째 페이지 샘플: {self.pages[0][:200]}...")
                
        except Exception as e:
            print(f"PDF 로드 오류: {e}")
            self.pages = []