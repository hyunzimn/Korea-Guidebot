# modules/query_engine.py
import os
import re
import json
import requests
from dotenv import load_dotenv
from modules.pdf_loader import PDFLoader
from modules.prompt_template import build_prompt

# 환경변수 로드
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# 한국어 조사를 제거하기 위한 suffix 목록
_JOSA_SUFFIXES = [
    '이라는', '라는', '란', '은', '는', '이', '가', '을', '를',
    '에', '에서', '으로', '로', '와', '과', '의', '도', '만'
]

def _extract_keywords(query: str) -> list:
    # 단어 추출
    raw = re.findall(r"[\w\uac00-\ud7af]+", query)
    kws = set(raw)
    # 조사(josa) 제거 후 뿌리 단어도 추가
    for w in raw:
        for j in _JOSA_SUFFIXES:
            if w.endswith(j) and len(w) > len(j):
                kws.add(w[:-len(j)])
    return list(kws)

def fuzzy_search(query: str, pages: list) -> list:
    if not pages or not query:
        return []
    keywords = _extract_keywords(query)
    scored = []
    for page in pages:
        score = sum(page.lower().count(kw.lower()) for kw in keywords)
        if score > 0:
            scored.append((score, page))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [pg for _, pg in scored[:3]]

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
        return "GROQ API 키가 설정되지 않았습니다."
    payload = {
        "model": "mistral-saba-24b",
        "temperature": 0.4,
        "messages": [
            {"role": "user", "content": aggressive_clean_text(prompt)}
        ],
        # 여기서 max_tokens → max_completion_tokens 로 변경
        "max_completion_tokens": 32768
    }
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        data=safe_json_encode(payload)
    )
    if resp.status_code != 200:
        return f"API 호출 오류: {resp.status_code}"
    return resp.json()['choices'][0]['message']['content'].strip()

class QueryEngine:
    def __init__(self, pdf_path: str, system_prompt: str):
        self.loader = PDFLoader(pdf_path)
        self.system_prompt = system_prompt

    def answer(self, user_query: str) -> str:
        pages = self.loader.pages
        relevant = fuzzy_search(user_query, pages)
        if not relevant:
            return "관련 정보를 찾을 수 없습니다."
        prompt = build_prompt(relevant, user_query)
        return safe_api_call(prompt)
