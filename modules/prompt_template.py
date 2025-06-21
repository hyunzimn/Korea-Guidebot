DEFAULT_PROMPT = """당신은 한국 생활 가이드 전문가입니다. 
제공된 문서 내용을 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 해주세요.

**답변 규칙:**
1. 문서에 있는 정보만을 사용하여 답변하세요
2. 정확한 정보를 자연스럽고 이해하기 쉽게 설명하세요
3. 단편적인 키워드 나열이 아닌 완전한 문장으로 답변하세요
4. 관련 정보가 부족하면 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요

**중요:** 답변은 반드시 완전한 문장으로 구성하고, 키워드만 나열하지 마세요."""


def build_prompt(context_pages: list, user_query: str) -> str:
    """완전한 페이지들을 컨텍스트로 사용하여 프롬프트 구성"""
    
    # 페이지들을 구분하여 컨텍스트 구성
    context_sections = []
    for i, page in enumerate(context_pages, 1):
        # 페이지 내용이 너무 짧으면 건너뛰기
        if len(page.strip()) < 50:
            continue
            
        context_sections.append(f"=== 문서 {i} ===\n{page.strip()}")
    
    if not context_sections:
        context = "관련 정보가 부족합니다."
    else:
        context = "\n\n".join(context_sections)
    
    prompt = f"""{DEFAULT_PROMPT}

=== 제공된 문서 내용 ===
{context}

=== 사용자 질문 ===
{user_query}

=== 답변 ===
"""
    
    return prompt