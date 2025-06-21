import os
import re
import json
import requests
from dotenv import load_dotenv
from modules.pdf_loader import PDFLoader
from modules.prompt_template import build_prompt

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

_JOSA_SUFFIXES = [
    '이라는', '라는', '란', '은', '는', '이', '가', '을', '를',
    '에', '에서', '으로', '로', '와', '과', '의', '도', '만'
]

def _extract_keywords(query: str) -> list:
    raw = re.findall(r"[\w\uac00-\ud7af]+", query)
    kws = set(raw)
    for w in raw:
        for j in _JOSA_SUFFIXES:
            if w.endswith(j) and len(w) > len(j):
                kws.add(w[:-len(j)])
    return list(kws)

def find_relevant_pages(query: str, pages: list) -> list:
    if not pages or not query:
        return []
    
    keywords = _extract_keywords(query)
    relevant_pages = []
    
    for page_idx, page in enumerate(pages):
        page_lower = page.lower()
        
        keyword_matches = []
        for keyword in keywords:
            if len(keyword) >= 2:
                if keyword.lower() in page_lower:
                    keyword_matches.append(keyword)
        
        if keyword_matches:
            match_count = sum(page_lower.count(kw.lower()) for kw in keyword_matches)
            relevant_pages.append((match_count, page_idx, page, keyword_matches))
    
    relevant_pages.sort(key=lambda x: x[0], reverse=True)
    
    selected_pages = []
    for _, page_idx, page, matches in relevant_pages[:3]:
        print(f"선택된 페이지 {page_idx}: 키워드 매치 {matches}")
        selected_pages.append(page)
    
    return selected_pages

def aggressive_clean_text(text: str) -> str:
    import unicodedata
    text = unicodedata.normalize('NFKD', text)
    for old, new in {
        "\u201c": '"', "\u201d": '"', "\u2018": "'", "\u2019": "'",
        "\u2013": '-', "\u2014": '-', "\u2026": '...',
        "\u00a0": ' ', "\u00ad": '', "\u200b": '', "\u200c": '',
        "\u200d": '', "\ufeff": ''
    }.items():
        text = text.replace(old, new)
    return re.sub(r"\s+", " ", text).strip()

def safe_json_encode(data):
    try:
        return json.dumps(data, ensure_ascii=False, separators=(',', ':'))
    except:
        return json.dumps(data, ensure_ascii=True)

def safe_api_call(prompt: str) -> str:
    if not GROQ_API_KEY:
        return "GROQ API 키가 설정되지 않았습니다. .env 파일에 GROQ_API_KEY를 설정해주세요."
    
    if not GROQ_API_KEY.startswith('gsk_'):
        return "GROQ API 키 형식이 올바르지 않습니다. 'gsk_'로 시작해야 합니다."

    #아래는 API 호출 오류로 인해 추가함.
    models_to_try = [
        "mistral-saba-24b",
        "llama-3.1-70b-versatile",
        "mixtral-8x7b-32768",
        "gemma2-9b-it"
    ]
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    for model in models_to_try:
        payload = {
            "model": model,
            "temperature": 0.4,
            "messages": [
                {"role": "user", "content": aggressive_clean_text(prompt)}
            ],
            "max_tokens": 8192  # max_completion_tokens 대신 max_tokens 사용
        }
        
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                data=safe_json_encode(payload),
                timeout=30
            )

            #디버깅용
            if resp.status_code == 400:
                error_detail = ""
                try:
                    error_json = resp.json()
                    error_detail = f"상세 오류: {error_json}"
                except:
                    error_detail = f"응답 내용: {resp.text}"
                
                print(f"모델 {model} 400 오류: {error_detail}")
                continue  # 다음 모델 시도
                
            elif resp.status_code == 401:
                return "API 키가 유효하지 않습니다. GROQ_API_KEY를 확인해주세요."
            elif resp.status_code == 429:
                return "API 호출 한도를 초과했습니다. 잠시 후 다시 시도해주세요."
            elif resp.status_code != 200:
                print(f"모델 {model} API 오류 {resp.status_code}: {resp.text}")
                continue  # 다음 모델 시도
            
            # 성공한 경우
            result = resp.json()
            if 'choices' in result and len(result['choices']) > 0:
                return result['choices'][0]['message']['content'].strip()
            else:
                continue  # 다음 모델 시도
                
        except requests.exceptions.RequestException as e:
            print(f"모델 {model} 네트워크 오류: {e}")
            continue
        except Exception as e:
            print(f"모델 {model} 기타 오류: {e}")
            continue
    
    return "모든 모델에서 API 호출에 실패했습니다. 네트워크 연결과 API 키를 확인해주세요."

class QueryEngine:
    def __init__(self, pdf_path: str, system_prompt: str):
        self.loader = PDFLoader(pdf_path)
        self.system_prompt = system_prompt

    def answer(self, user_query: str) -> str:
        pages = self.loader.pages
        if not pages:
            return "PDF 파일을 로드할 수 없습니다. 파일 경로를 확인해주세요."
        
        print(f"총 {len(pages)}개 페이지 로드됨")
        print(f"사용자 질문: {user_query}")
        
        relevant_pages = find_relevant_pages(user_query, pages)
        
        if not relevant_pages:
            return "질문과 관련된 정보를 PDF에서 찾을 수 없습니다."
        
        print(f"관련 페이지 {len(relevant_pages)}개 발견")
        
        prompt = build_prompt(relevant_pages, user_query)
        
        # 디버깅용 (프롬프트 길이 확인)
        print(f"생성된 프롬프트 길이: {len(prompt)} 문자")
        
        return safe_api_call(prompt)
