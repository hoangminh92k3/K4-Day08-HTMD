import streamlit as st
import os
from dotenv import load_dotenv
from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="IELTS RAG Chatbot",
    page_icon="📚",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.title("⚙️ Cấu hình Hệ thống")
    st.caption("Chatbot hỗ trợ hỏi đáp IELTS Writing")
    
    # Feature for Huy: LLM Provider selection
    llm_provider = st.selectbox(
        "Chọn LLM Provider", 
        ["openai", "gemini", "anthropic", "cohere", "groq"],
        index=3  # Default to cohere which Huy added
    )
    os.environ["LLM_PROVIDER"] = llm_provider
    
    top_k = st.slider("Số lượng Chunks truy xuất (top_k)", 1, 10, 5)
    
    if st.button("Xóa Lịch sử Chat"):
        st.session_state.messages = []
        st.rerun()

st.title("📚 IELTS Writing AI Assistant")
st.caption("Nhập câu hỏi liên quan đến tiêu chí chấm điểm hoặc mẹo viết IELTS.")

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "sources" in message and message["sources"]:
            with st.expander(f"Nguồn tham khảo ({message.get('retrieval_source', 'hybrid')})"):
                for idx, src in enumerate(message["sources"]):
                    st.markdown(f"**[{idx+1}] {src['metadata']['title']}** (Score: {src['score']:.4f})")

query = st.chat_input("Nhập câu hỏi của bạn tại đây...")

if query:
    # Lưu và hiển thị câu hỏi của user
    st.session_state.messages.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    # Hiển thị phản hồi của assistant
    with st.chat_message("assistant"):
        with st.spinner("Đang tìm kiếm tài liệu và tạo câu trả lời..."):
            try:
                result = generate_with_citation(query, top_k=top_k)
                answer = result["answer"]
                sources = result["sources"]
                r_source = result["retrieval_source"]
                
                st.markdown(answer)
                
                if sources:
                    with st.expander(f"Nguồn tham khảo ({r_source})"):
                        for idx, src in enumerate(sources):
                            st.markdown(f"**[{idx+1}] {src['metadata']['title']}** (Score: {src['score']:.4f})")
                
                # Lưu vào lịch sử
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "sources": sources,
                    "retrieval_source": r_source
                })
            except Exception as e:
                st.error(f"Đã xảy ra lỗi hệ thống: {str(e)}")
