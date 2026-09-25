import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation

load_dotenv()

st.set_page_config(
    page_title="IELTS Writing Assistant",
    page_icon="✍️",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_sources(sources: list[dict], retrieval_source: str) -> None:
    """Render traceable retrieval evidence for an answer."""
    if not sources:
        st.info("Không có nguồn phù hợp trong corpus để xác minh câu trả lời này.")
        return

    label = "PageIndex fallback" if retrieval_source == "pageindex" else "Hybrid retrieval"
    with st.expander(f"Nguồn đã dùng ({len(sources)}) — {label}", expanded=False):
        for index, source in enumerate(sources, 1):
            metadata = source["metadata"]
            title = metadata["title"]
            url = metadata.get("url")
            source_label = metadata["source"]
            score = float(source["score"])
            method = source["retrieval_method"]
            if url:
                st.markdown(f"{index}. [{title}]({url})")
            else:
                st.markdown(f"{index}. **{title}**")
            st.caption(f"`{source_label}` · {method} · score {score:.4f}")


with st.sidebar:
    st.title("IELTS Writing Assistant")
    st.caption("Hỏi đáp có căn cứ về tiêu chí và cách chuẩn bị IELTS Writing.")
    top_k = st.slider("Số chunks", 3, 10, 5)

st.title("IELTS Writing Assistant")
st.caption("Câu trả lời chỉ dùng corpus IELTS của nhóm và luôn hiển thị nguồn truy xuất.")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant":
            render_sources(
                message.get("sources", []), message.get("retrieval_source", "none")
            )

query = st.chat_input("Nhập câu hỏi...")

if query:
    st.session_state.messages.append({"role": "user", "content": query})

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        result = generate_with_citation(query, top_k=top_k)
        st.markdown(result["answer"])
        render_sources(result["sources"], result["retrieval_source"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "sources": result["sources"],
            "retrieval_source": result["retrieval_source"],
        }
    )
