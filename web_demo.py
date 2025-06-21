import gradio as gr

from modules.query_engine import QueryEngine
from modules.prompt_template import DEFAULT_PROMPT

# 내장된 PDF 파일 경로
PDF_PATH = "data/guide.pdf"

# 챗봇 엔진 초기화
engine = QueryEngine(PDF_PATH, DEFAULT_PROMPT)

def ask_question(question: str) -> str:
    if not question:
        return "질문을 입력해주세요."
    return engine.answer(question)

with gr.Blocks() as demo:
    gr.Markdown("## 한국생활가이드 챗봇")
    question_input = gr.Textbox(label="질문", lines=1, placeholder="여기에 질문을 입력하세요.")
    ask_btn = gr.Button("질문하기", variant="primary")
    answer_output = gr.Textbox(label="답변", lines=10, interactive=False)

    ask_btn.click(
        ask_question,
        inputs=[question_input],
        outputs=[answer_output]
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=30987)