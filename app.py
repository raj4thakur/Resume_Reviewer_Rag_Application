import streamlit as st

from src.review_agent import ReviewError, review_resume
from src.resume_parser import extract_text_from_upload


st.set_page_config(
    page_title="Resume Reviewer AI",
    page_icon="📄",
    layout="wide",
)

st.markdown(
    """
    <style>
    .block-container { max-width: 1100px; padding-top: 2rem; }
    .score-card {
        padding: 1rem 1.2rem; border: 1px solid rgba(128,128,128,.25);
        border-radius: 14px; text-align: center;
    }
    .score { font-size: 2.2rem; font-weight: 700; }
    .muted { color: #777; font-size: .9rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📄 Resume Reviewer AI")
st.caption("AI-powered resume ↔ job-description analysis using NVIDIA Nemotron.")

with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. Upload your resume\n"
        "2. Upload/paste the job description\n"
        "3. NVIDIA Nemotron analyzes the match\n"
        "4. Get ATS gaps, strengths, and actionable improvements"
    )
    st.divider()
    st.caption("Your NVIDIA API key stays server-side in Render environment variables.")

resume_file = st.file_uploader(
    "Resume",
    type=["pdf", "docx", "txt"],
    help="PDF, DOCX, or TXT",
)
jd_file = st.file_uploader(
    "Job description",
    type=["pdf", "docx", "txt"],
    help="PDF, DOCX, or TXT",
)

jd_text = st.text_area(
    "Or paste the job description",
    height=180,
    placeholder="Paste the job description here if you do not want to upload a file.",
)

review_clicked = st.button(
    "🔍 Review Resume",
    type="primary",
    use_container_width=True,
)

if review_clicked:
    if not resume_file:
        st.error("Please upload a resume.")
        st.stop()

    if not jd_file and not jd_text.strip():
        st.error("Upload a job description or paste it in the text box.")
        st.stop()

    try:
        with st.spinner("Extracting documents and asking Nemotron to review them..."):
            resume_text = extract_text_from_upload(resume_file)
            if jd_file:
                jd_text = extract_text_from_upload(jd_file)
            result = review_resume(resume_text, jd_text)

        st.success("Review complete.")

        score_cols = st.columns(2)
        for col, label, value in [
            (score_cols[0], "Overall match", result["overall_score"]),
            (score_cols[1], "ATS compatibility", result["ats_score"]),
        ]:
            with col:
                st.markdown(
                    f'<div class="score-card"><div class="muted">{label}</div>'
                    f'<div class="score">{value}/100</div></div>',
                    unsafe_allow_html=True,
                )

        st.divider()

        left, right = st.columns(2)

        with left:
            st.subheader("✅ Strengths")
            for item in result["strengths"]:
                st.markdown(f"- {item}")

            st.subheader("⚠️ Gaps")
            for item in result["gaps"]:
                st.markdown(f"- {item}")

            st.subheader("🔑 Keyword analysis")
            for item in result["keyword_analysis"]:
                st.markdown(f"- {item}")

        with right:
            st.subheader("🚀 Recommendations")
            for item in result["recommendations"]:
                st.markdown(f"- {item}")

            st.subheader("🎯 Interview focus")
            for item in result["interview_focus"]:
                st.markdown(f"- {item}")

            st.subheader("✍️ Suggested professional summary")
            st.info(result["rewritten_summary"])

        with st.expander("View extracted resume text"):
            st.text(resume_text)

    except ReviewError as exc:
        st.error(str(exc))
    except Exception:
        st.error("Something went wrong while processing the review. Check the Render logs.")
