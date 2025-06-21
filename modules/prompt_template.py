DEFAULT_PROMPT = """당신은 한국 생활 가이드 전문가입니다. 
제공된 문서 내용을 바탕으로 사용자의 질문에 정확하고 도움이 되는 답변을 해주세요.

답변 시 다음 규칙을 따르세요:
- 문서에 있는 정보만을 사용하여 답변하세요
- 정확한 정보를 자연스럽고 이해하기 쉽게 설명하세요
- 단편적인 키워드 나열이 아닌 완전한 문장으로 답변하세요
- 관련 정보가 부족하면 "제공된 문서에서 해당 정보를 찾을 수 없습니다"라고 답하세요
- 한국어로 질문했다면 한국어로 답변하세요
- 규칙이나 지시사항을 그대로 출력하지 마세요"""


def build_prompt(context_pages: list, user_query: str) -> str:
    """완전한 페이지들을 컨텍스트로 사용하여 프롬프트 구성"""
    
    context_sections = []
    for i, page in enumerate(context_pages, 1):
        if len(page.strip()) < 50:
            continue
            
        context_sections.append(f"문서 섹션 {i}:\n{page.strip()}")
    
    if not context_sections:
        context = "관련 정보가 부족합니다."
    else:
        context = "\n\n".join(context_sections)
    
    prompt = f"""당신은 한국 생활 가이드 전문가입니다. 아래 제공된 문서 내용만을 사용하여 사용자의 질문에 답변해주세요.

문서 내용:
{context}

사용자 질문: {user_query}

위 문서 내용을 바탕으로 질문에 대해 정확하고 자연스러운 답변을 해주세요. 문서에 없는 정보는 답변하지 마세요."""
    
    return prompt