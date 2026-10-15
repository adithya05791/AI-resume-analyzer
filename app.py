import streamlit as st

from resume_analyzer.pdf_reader import extract_text_from_pdf
from resume_analyzer.pipeline import analyze

SAMPLE_JOB = (
    "We are hiring a Python Developer with experience in Python, Flask, Angular, "
    "SQL, Docker, and Machine Learning. The candidate should have experience "
    "developing web applications and working in software development teams."
)

st.set_page_config(page_title="AI Resume Analyzer", page_icon="📄", layout="centered")
with st.sidebar:
    st.header("How it works")
    st.markdown(
        "1. Upload a text-based PDF resume.\n"
        "2. Paste a job description.\n"
        "3. The app finds known skills in both and compares them.\n\n"
        "**Limits:** only skills in the built-in list are detected, and scanned "
        "PDFs can't be read."
    )


def use_sample_job():
    st.session_state["job_text"] = SAMPLE_JOB


def build_report(result: dict, filename: str) -> str:
    lines = [
        "AI Resume Analyzer report",
        f"Resume file: {filename}",
        "",
        f"Skill coverage: {result['coverage']:.0f}%",
        f"Text similarity: {result['similarity']:.0f}%",
        "",
        "Required skills detected in the job description:",
        ", ".join(result["required"]) or "None",
        "",
        "Matched skills:",
        ", ".join(result["matched"]) or "None",
        "",
        "Skills not detected in the resume:",
        ", ".join(result["missing"]) or "None",
    ]
    return "\n".join(lines)


st.title("📄 AI Resume Analyzer")
st.caption("Compare your resume with a job description · Version 2")

st.subheader("1. Upload your resume")
uploaded = st.file_uploader("PDF resume", type="pdf")

st.subheader("2. Paste the job description")
st.button("Use sample job description", on_click=use_sample_job)
job_text = st.text_area(
    "Job description",
    key="job_text",
    height=220,
    placeholder="Paste the full job description here...",
)

if st.button("Analyze resume", type="primary"):
    if uploaded is None:
        st.warning("Please upload a PDF resume first.")
    elif not job_text.strip():
        st.warning("Please paste a job description.")
    else:
        try:
            with st.spinner("Analyzing your resume..."):
                resume_text = extract_text_from_pdf(uploaded.getvalue())
                result = analyze(resume_text, job_text) if resume_text.strip() else None
        except Exception as exc:
            st.session_state.pop("result", None)
            st.error(f"Could not read this PDF ({type(exc).__name__}). Try another file.")
        else:
            if result is None:
                st.session_state.pop("result", None)
                st.error("No text found. The PDF may be a scanned image. Try a text-based PDF.")
            else:
                st.session_state["result"] = result
                st.session_state["result_file"] = uploaded.name

result = st.session_state.get("result")
if result:
    st.divider()
    st.subheader("Analysis results")

    c1, c2, c3 = st.columns(3)
    c1.metric("Skill coverage", f"{result['coverage']:.0f}%")
    c2.metric(
        "Text similarity",
        f"{result['similarity']:.0f}%",
        help="Word overlap between your resume and the job text. It is usually low "
        "for short job descriptions, so treat skill coverage as the main signal.",
    )
    c3.metric("Skills required", len(result["required"]))

    if not result["required"]:
        st.warning(
            "No known skills were detected in the job description, so coverage can't be "
            "calculated. Try a description that names specific technologies."
        )
    else:
        st.progress(int(result["coverage"]))
        left, right = st.columns(2)
        with left:
            st.markdown("**Matched skills**")
            if result["matched"]:
                for skill in result["matched"]:
                    st.markdown(f"✅ {skill}")
            else:
                st.markdown("None")
        with right:
            st.markdown("**Not detected in resume**")
            if result["missing"]:
                for skill in result["missing"]:
                    st.markdown(f"❌ {skill}")
            else:
                st.markdown("None 🎉")
        if result["missing"]:
            st.info("Only add a missing skill to your resume if you genuinely have it.")

    st.download_button(
        "Download report (.txt)",
        data=build_report(result, st.session_state.get("result_file", "resume.pdf")),
        file_name="resume_analysis.txt",
        mime="text/plain",
    )
    st.caption(
        "Text similarity compares wording only; it is not a prediction of being hired. "
        "Only skills listed in data/skills.json are detected."
    )