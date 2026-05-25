import streamlit as st
from agent import runAgent
from quote import generateQuotePdf

st.set_page_config(page_title="AI Sales Agent", page_icon="🤖", layout="centered")

st.title("🤖 Autonomous Sales Engineer")
st.caption("Powered by Gemini + Tavily")

# Input form
with st.form("brief_form"):
    brief = st.text_area(
        "Enter your client brief:",
        placeholder="e.g. I need a minimalist home office for a 10x10ft room in Kuala Lumpur, budget RM3,000",
        height=100
    )
    submitted = st.form_submit_button("Generate Quote", use_container_width=True)

if submitted and brief:
    with st.spinner("Agent is working... this may take 30-60 seconds"):
        result = runAgent(brief)

    st.success("✅ Quote generated!")
    st.markdown("### 📋 Proposed Solution")
    st.markdown(result)

    # PDF download
    st.markdown("---")
    pdfPath = generateQuotePdf(brief, result, "quote.pdf")
    with open(pdfPath, "rb") as f:
        st.download_button(
            label="📥 Download PDF Quote",
            data=f,
            file_name="sales_quote.pdf",
            mime="application/pdf",
            use_container_width=True
        )