# Korea-Guidebot 🤖🇰🇷
한국에서 생활하는 외국인들을 위한 '한국생활가이드 2021'(https://openknowledge.kotra.or.kr/handle/2014.oak/25569) 문서를 바탕으로 하는 챗봇입니다.

## 시스템 구조

```text
.
├── modules/
│   ├── pdf_loader.py       # PDF 로딩 및 텍스트 추출
│   ├── query_engine.py     # 검색 엔진 및 API 호출
│   └── prompt_template.py  # 프롬프트 템플릿 관리
├── data/
│   └── guide.pdf           # 가이드 PDF 파일
├── web_demo.py             # Gradio 웹 데모
├── requirements.txt        # 패키지 의존성
└── .env                    # 환경변수 (API 키)
```

## 사용 방법

### 1. 환경변수 설정
.env 파일을 생성하고 Groq API 키를 설정합니다:
```
GROQ_API_KEY=gsk_your_actual_api_key_here
```

### 2. 의존성 설치
```
pip install -r requirements.txt
```

### 3. 순서대로 입력 (한글 입출력을 도와줍니다)
```
export PYTHONUTF8=1,
export LANG=ko_KR.UTF-8,
export LC_ALL=ko_KR.UTF-8
```

### 4. 웹 데모 실행
```
python web_demo.py
```
