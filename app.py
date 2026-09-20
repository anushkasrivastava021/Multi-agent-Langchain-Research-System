import streamlit as st

from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Autonomous Research Agent",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================
# SESSION STATE
# =========================================================

if "run_research" not in st.session_state:
    st.session_state.run_research = False

if "scroll_to_processing" not in st.session_state:
    st.session_state.scroll_to_processing = False

if "last_topic" not in st.session_state:
    st.session_state.last_topic = ""


# =========================================================
# HELPERS
# =========================================================

def clean_output(output):
    """
    Convert LangChain / agent output into clean text.
    """

    if output is None:
        return ""

    # LangChain AIMessage / HumanMessage / BaseMessage
    if hasattr(output, "content"):
        return str(output.content)

    # Dictionary output
    if isinstance(output, dict):
        if "content" in output:
            return str(output["content"])

        if "messages" in output:
            messages = output["messages"]

            if isinstance(messages, list) and messages:
                last_message = messages[-1]

                if hasattr(last_message, "content"):
                    return str(last_message.content)

                return str(last_message)

        return str(output)

    # List / tuple output
    if isinstance(output, (list, tuple)):
        parts = []

        for item in output:
            if hasattr(item, "content"):
                parts.append(str(item.content))
            else:
                parts.append(str(item))

        return "\n\n".join(parts)

    return str(output)


def ui_html(content):
    """
    Render HTML safely inside Streamlit.
    Keeping HTML strings compact prevents Streamlit
    from treating indented HTML as a code block.
    """
    st.markdown(content, unsafe_allow_html=True)


# =========================================================
# ENTER KEY CALLBACK
# =========================================================

def start_from_enter():

    topic = st.session_state.topic_input.strip()

    if topic:
        st.session_state.run_research = True
        st.session_state.scroll_to_processing = True
        st.session_state.last_topic = topic


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
<style>

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');


/* =====================================================
   GLOBAL
   ===================================================== */

html {
    scroll-behavior: smooth;
}

.stApp {
    background:
        radial-gradient(
            circle at 10% 10%,
            rgba(99, 102, 241, 0.18),
            transparent 30%
        ),
        radial-gradient(
            circle at 90% 20%,
            rgba(168, 85, 247, 0.15),
            transparent 28%
        ),
        radial-gradient(
            circle at 50% 90%,
            rgba(14, 165, 233, 0.12),
            transparent 30%
        ),
        #070914;

    color: #f8fafc;
    font-family: 'Inter', sans-serif;

    min-height: 100vh;
    overflow-x: hidden;
}


/* =====================================================
   ANIMATED AURORA
   ===================================================== */

.stApp::before {
    content: "";
    position: fixed;
    inset: -30%;
    z-index: -2;

    background:
        radial-gradient(
            circle at 20% 30%,
            rgba(99, 102, 241, 0.22),
            transparent 25%
        ),
        radial-gradient(
            circle at 80% 20%,
            rgba(168, 85, 247, 0.18),
            transparent 25%
        ),
        radial-gradient(
            circle at 50% 80%,
            rgba(14, 165, 233, 0.15),
            transparent 25%
        );

    filter: blur(70px);

    animation: auroraMove 16s ease-in-out infinite alternate;
    pointer-events: none;
}


@keyframes auroraMove {

    0% {
        transform: translate3d(-3%, -2%, 0) scale(1);
    }

    50% {
        transform: translate3d(4%, 3%, 0) scale(1.08);
    }

    100% {
        transform: translate3d(-2%, 5%, 0) scale(1.03);
    }
}


/* =====================================================
   SIDEBAR
   ===================================================== */

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            180deg,
            rgba(12, 15, 30, 0.97),
            rgba(8, 10, 22, 0.97)
        );

    border-right: 1px solid rgba(255,255,255,0.08);
}


[data-testid="stSidebar"] * {
    color: #e5e7eb;
}


/* =====================================================
   HERO
   ===================================================== */

.hero-container {
    padding: 45px 10px 25px 10px;
    text-align: center;
}


.hero-badge {
    display: inline-block;

    padding: 8px 16px;

    border-radius: 999px;

    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,0.18),
            rgba(168,85,247,0.18)
        );

    border: 1px solid rgba(129,140,248,0.28);

    color: #c4b5fd;

    font-size: 13px;
    font-weight: 600;

    margin-bottom: 18px;

    box-shadow:
        0 0 30px rgba(99,102,241,0.08);
}


.hero-title {
    font-size: clamp(38px, 6vw, 70px);

    font-weight: 800;

    line-height: 1.05;

    margin: 0;

    background:
        linear-gradient(
            90deg,
            #818cf8,
            #c084fc,
            #38bdf8,
            #818cf8
        );

    background-size: 300% auto;

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;

    animation: gradientText 7s linear infinite;
}


@keyframes gradientText {

    0% {
        background-position: 0% center;
    }

    100% {
        background-position: 300% center;
    }
}


.hero-subtitle {
    max-width: 720px;

    margin: 18px auto 0;

    color: #94a3b8;

    font-size: 16px;

    line-height: 1.7;
}


/* =====================================================
   INPUT AREA
   ===================================================== */

.search-wrapper {
    max-width: 900px;

    margin: 25px auto 30px;

    padding: 8px;

    border-radius: 18px;

    background:
        linear-gradient(
            135deg,
            rgba(99,102,241,0.14),
            rgba(168,85,247,0.10)
        );

    border: 1px solid rgba(255,255,255,0.08);

    box-shadow:
        0 20px 70px rgba(0,0,0,0.25);
}


div[data-testid="stTextInput"] input {

    background: rgba(15,23,42,0.78) !important;

    color: #f8fafc !important;

    border: 1px solid rgba(129,140,248,0.25) !important;

    border-radius: 13px !important;

    padding: 17px 18px !important;

    font-size: 16px !important;

    transition: all 0.25s ease;
}


div[data-testid="stTextInput"] input:focus {

    border-color: rgba(129,140,248,0.75) !important;

    box-shadow:
        0 0 0 3px rgba(99,102,241,0.12),
        0 0 35px rgba(99,102,241,0.12) !important;
}


/* =====================================================
   START BUTTON
   ===================================================== */

div.stButton > button {

    width: 100%;

    min-height: 56px;

    border: none;

    border-radius: 14px;

    color: white;

    font-size: 16px;

    font-weight: 700;

    background:
        linear-gradient(
            90deg,
            #6366f1,
            #8b5cf6,
            #06b6d4,
            #6366f1
        );

    background-size: 300% auto;

    animation: buttonGradient 6s linear infinite;

    box-shadow:
        0 10px 35px rgba(99,102,241,0.22);

    transition:
        transform 0.25s ease,
        box-shadow 0.25s ease;
}


div.stButton > button:hover {

    transform: translateY(-3px);

    box-shadow:
        0 16px 45px rgba(99,102,241,0.35);
}


@keyframes buttonGradient {

    0% {
        background-position: 0% center;
    }

    100% {
        background-position: 300% center;
    }
}


/* =====================================================
   PIPELINE
   ===================================================== */

.pipeline-card {

    min-height: 185px;

    padding: 25px;

    border-radius: 20px;

    background:
        linear-gradient(
            145deg,
            rgba(20,24,45,0.82),
            rgba(10,13,28,0.78)
        );

    border: 1px solid rgba(255,255,255,0.08);

    backdrop-filter: blur(18px);

    box-shadow:
        0 15px 45px rgba(0,0,0,0.20);

    transition:
        transform 0.3s ease,
        border-color 0.3s ease,
        box-shadow 0.3s ease;

    position: relative;

    overflow: hidden;
}


.pipeline-card::before {

    content: "";

    position: absolute;

    inset: 0;

    background:
        linear-gradient(
            120deg,
            transparent,
            rgba(129,140,248,0.07),
            transparent
        );

    transform: translateX(-100%);

    transition: transform 0.6s ease;
}


.pipeline-card:hover {

    transform: translateY(-6px);

    border-color:
        rgba(129,140,248,0.35);

    box-shadow:
        0 20px 55px rgba(99,102,241,0.16);
}


.pipeline-card:hover::before {

    transform: translateX(100%);
}


.pipeline-icon {

    font-size: 34px;

    margin-bottom: 15px;
}


.pipeline-number {

    font-size: 11px;

    letter-spacing: 2px;

    color: #818cf8;

    font-weight: 700;

    margin-bottom: 7px;
}


.pipeline-title {

    font-size: 19px;

    font-weight: 700;

    color: #f8fafc;

    margin-bottom: 8px;
}


.pipeline-description {

    font-size: 13px;

    line-height: 1.6;

    color: #94a3b8;
}


/* =====================================================
   SECTION HEADINGS
   ===================================================== */

.section-heading {

    margin: 50px 0 20px;

    padding-left: 15px;

    border-left: 3px solid #818cf8;

    font-size: 22px;

    font-weight: 750;

    color: #f8fafc;
}


/* =====================================================
   DIVIDER
   ===================================================== */

.gradient-divider {

    height: 1px;

    width: 100%;

    margin: 35px 0;

    background:
        linear-gradient(
            90deg,
            transparent,
            rgba(129,140,248,0.45),
            rgba(192,132,252,0.45),
            transparent
        );
}


/* =====================================================
   RESULT CARDS
   ===================================================== */

.result-card {

    padding: 25px;

    border-radius: 18px;

    background:
        rgba(15,23,42,0.72);

    border:
        1px solid rgba(255,255,255,0.07);

    box-shadow:
        0 15px 45px rgba(0,0,0,0.16);

    margin-bottom: 20px;
}


.result-title {

    font-size: 17px;

    font-weight: 700;

    margin-bottom: 12px;

    color: #e2e8f0;
}


/* =====================================================
   EMPTY STATE
   ===================================================== */

.empty-state {

    text-align: center;

    padding: 55px 20px;

    margin-top: 30px;

    border-radius: 22px;

    border:
        1px dashed rgba(129,140,248,0.20);

    background:
        rgba(15,23,42,0.38);
}


.empty-icon {

    font-size: 48px;

    margin-bottom: 15px;
}


.empty-title {

    font-size: 20px;

    font-weight: 700;

    color: #e2e8f0;

    margin-bottom: 8px;
}


.empty-text {

    color: #64748b;

    font-size: 14px;
}


/* =====================================================
   METRICS
   ===================================================== */

.metric-card {

    padding: 20px;

    border-radius: 16px;

    background:
        rgba(15,23,42,0.65);

    border:
        1px solid rgba(255,255,255,0.07);

    text-align: center;
}


.metric-value {

    font-size: 27px;

    font-weight: 800;

    color: #c4b5fd;
}


.metric-label {

    margin-top: 5px;

    font-size: 12px;

    color: #64748b;
}


/* =====================================================
   EXPANDERS
   ===================================================== */

div[data-testid="stExpander"] {

    background:
        rgba(15,23,42,0.58);

    border:
        1px solid rgba(255,255,255,0.07);

    border-radius: 16px;

    overflow: hidden;
}


/* =====================================================
   STATUS
   ===================================================== */

div[data-testid="stStatus"] {

    border-radius: 16px !important;

    border:
        1px solid rgba(129,140,248,0.14) !important;

    background:
        rgba(15,23,42,0.58) !important;
}


/* =====================================================
   DOWNLOAD BUTTON
   ===================================================== */

div[data-testid="stDownloadButton"] button {

    border-radius: 12px;

    border:
        1px solid rgba(129,140,248,0.25);

    background:
        rgba(99,102,241,0.10);

    color: #c4b5fd;

    font-weight: 600;
}


/* =====================================================
   FOOTER
   ===================================================== */

.footer {

    text-align: center;

    color: #475569;

    font-size: 12px;

    padding: 45px 0 25px;
}


/* =====================================================
   MOBILE
   ===================================================== */

@media (max-width: 768px) {

    .hero-title {
        font-size: 40px;
    }

    .hero-container {
        padding-top: 25px;
    }

    .pipeline-card {
        margin-bottom: 15px;
    }

}

</style>
""",
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    ui_html(
        '<div style="font-size:24px;font-weight:800;'
        'margin-bottom:8px;">🔬 Research Lab</div>'
    )

    ui_html(
        '<div style="color:#64748b;font-size:13px;'
        'line-height:1.6;margin-bottom:25px;">'
        'Autonomous multi-agent research system.'
        '</div>'
    )

    st.markdown("### ⚙️ Pipeline")

    st.markdown(
        """
        **1. 🔎 Search Agent**  
        Finds relevant sources.

        **2. 📖 Reader Agent**  
        Extracts useful information.

        **3. ✍️ Writer Agent**  
        Generates the research report.

        **4. 🧠 Critic Agent**  
        Evaluates the final report.
        """
    )

    st.markdown("---")

    st.caption("Powered by LangChain + Streamlit")


# =========================================================
# HERO
# =========================================================

ui_html(
    '<div class="hero-container">'
    '<div class="hero-badge">✦ AUTONOMOUS AI RESEARCH</div>'
    '<h1 class="hero-title">Research Anything.</h1>'
    '<div class="hero-subtitle">'
    'A multi-agent research system that searches, reads, writes, '
    'and critically evaluates information automatically.'
    '</div>'
    '</div>'
)


# =========================================================
# SEARCH INPUT
# =========================================================

st.markdown('<div class="search-wrapper">', unsafe_allow_html=True)

topic = st.text_input(
    "Research topic",
    placeholder="e.g. Impact of Generative AI on software development",
    label_visibility="collapsed",
    key="topic_input",
    on_change=start_from_enter,
)

st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# START RESEARCH BUTTON
# =========================================================

button_clicked = st.button(
    "🚀  Start Research",
    use_container_width=True,
)


if button_clicked:

    if topic.strip():

        st.session_state.run_research = True
        st.session_state.scroll_to_processing = True
        st.session_state.last_topic = topic.strip()

    else:

        st.warning("Please enter a research topic first.")


# =========================================================
# PIPELINE PREVIEW
# =========================================================

ui_html(
    '<div class="section-heading">⚡ How it works</div>'
)

pipeline_cols = st.columns(4)


pipeline_data = [
    (
        "🔎",
        "01",
        "Search Agent",
        "Searches the web and discovers relevant sources."
    ),
    (
        "📖",
        "02",
        "Reader Agent",
        "Scrapes the most relevant resources and extracts knowledge."
    ),
    (
        "✍️",
        "03",
        "Writer Agent",
        "Combines the collected information into a structured report."
    ),
    (
        "🧠",
        "04",
        "Critic Agent",
        "Reviews the report for quality, completeness and accuracy."
    ),
]


for col, data in zip(pipeline_cols, pipeline_data):

    icon, number, name, description = data

    with col:

        ui_html(
            f'<div class="pipeline-card">'
            f'<div class="pipeline-icon">{icon}</div>'
            f'<div class="pipeline-number">STAGE {number}</div>'
            f'<div class="pipeline-title">{name}</div>'
            f'<div class="pipeline-description">{description}</div>'
            f'</div>'
        )


# =========================================================
# PROCESSING SECTION
# =========================================================

if st.session_state.run_research:

    ui_html(
        '<div class="gradient-divider"></div>'
    )

    ui_html(
        '<div class="section-heading" id="processing-section">'
        '⚡ Research in progress'
        '</div>'
    )

    # -----------------------------------------------------
    # AUTO SCROLL
    # Works for BOTH:
    #   - pressing Enter
    #   - clicking Start Research
    # -----------------------------------------------------

    if st.session_state.scroll_to_processing:

        st.html(
            """
            <div id="research-processing-anchor"></div>

            <script>
            setTimeout(function() {

                const anchor =
                    document.getElementById(
                        "research-processing-anchor"
                    );

                if (anchor) {

                    anchor.scrollIntoView({
                        behavior: "smooth",
                        block: "start"
                    });

                }

            }, 200);
            </script>
            """,
            unsafe_allow_javascript=True,
        )

        st.session_state.scroll_to_processing = False


    # =====================================================
    # PROGRESS
    # =====================================================

    progress_bar = st.progress(0)

    topic_to_research = st.session_state.last_topic or topic.strip()

    if not topic_to_research:

        st.warning("Please enter a topic.")
        st.session_state.run_research = False
        st.stop()


    # =====================================================
    # STEP 1 — SEARCH AGENT
    # =====================================================

    with st.status(
        "🔎 Search Agent — finding relevant sources...",
        expanded=True,
    ) as search_status:

        search_agent = build_search_agent()

        search_results = search_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"Search for information on {topic_to_research}",
                    )
                ]
            }
        )

        search_text = clean_output(search_results)

        progress_bar.progress(25)

        search_status.update(
            label="🔎 Search Agent — completed",
            state="complete",
            expanded=False,
        )


    # =====================================================
    # STEP 2 — READER AGENT
    # =====================================================

    with st.status(
        "📖 Reader Agent — scraping top resources...",
        expanded=True,
    ) as reader_status:

        reader_agent = build_reader_agent()

        reader_results = reader_agent.invoke(
            {
                "messages": [
                    (
                        "user",
                        f"""
Based on the search results, scrape the top resources and extract
relevant information for the topic:

{topic_to_research}

Pick the most relevant information and summarize it concisely.

Search Results:

{search_text[:8000]}
""",
                    )
                ]
            }
        )

        scraped_text = clean_output(reader_results)

        progress_bar.progress(50)

        reader_status.update(
            label="📖 Reader Agent — completed",
            state="complete",
            expanded=False,
        )


    # =====================================================
    # STEP 3 — WRITER
    # =====================================================

    with st.status(
        "✍️ Writer Agent — generating research report...",
        expanded=True,
    ) as writer_status:

        research_combined = (
            f"SEARCH RESULTS:\n"
            f"{search_text}\n\n"
            f"DETAILED SCRAPED CONTENT:\n"
            f"{scraped_text}"
        )

        research_report = writer_chain.invoke(
            {
                "topic": topic_to_research,
                "research": research_combined,
            }
        )

        research_report = clean_output(research_report)

        progress_bar.progress(75)

        writer_status.update(
            label="✍️ Writer Agent — completed",
            state="complete",
            expanded=False,
        )


    # =====================================================
    # STEP 4 — CRITIC
    # =====================================================

    with st.status(
        "🧠 Critic Agent — evaluating the report...",
        expanded=True,
    ) as critic_status:

        report_evaluation = critic_chain.invoke(
            {
                "report": research_report,
            }
        )

        report_evaluation = clean_output(report_evaluation)

        progress_bar.progress(100)

        critic_status.update(
            label="🧠 Critic Agent — completed",
            state="complete",
            expanded=False,
        )


    # =====================================================
    # COMPLETE
    # =====================================================

    st.success(
        "🎉 Research completed successfully!"
    )


    # =====================================================
    # RESULTS
    # =====================================================

    ui_html(
        '<div class="gradient-divider"></div>'
    )

    ui_html(
        '<div class="section-heading">'
        '📑 Research Results'
        '</div>'
    )


    # =====================================================
    # METRICS
    # =====================================================

    metric_cols = st.columns(3)

    with metric_cols[0]:

        ui_html(
            '<div class="metric-card">'
            '<div class="metric-value">4</div>'
            '<div class="metric-label">AI Agents / Stages</div>'
            '</div>'
        )

    with metric_cols[1]:

        ui_html(
            '<div class="metric-card">'
            f'<div class="metric-value">'
            f'{len(search_text):,}'
            f'</div>'
            '<div class="metric-label">Search Characters</div>'
            '</div>'
        )

    with metric_cols[2]:

        ui_html(
            '<div class="metric-card">'
            f'<div class="metric-value">'
            f'{len(research_report):,}'
            f'</div>'
            '<div class="metric-label">Report Characters</div>'
            '</div>'
        )


    # =====================================================
    # FINAL REPORT
    # =====================================================

    st.markdown("### 📄 Final Research Report")

    ui_html(
        '<div class="result-card">'
        f'<div class="result-title">'
        f'🔬 {topic_to_research}'
        f'</div>'
        '</div>'
    )

    st.markdown(research_report)


    # =====================================================
    # DOWNLOAD REPORT
    # =====================================================

    st.download_button(
        label="⬇️ Download Research Report",
        data=research_report,
        file_name=(
            f"{topic_to_research[:50]}"
            .replace(" ", "_")
            .replace("/", "_")
            + ".txt"
        ),
        mime="text/plain",
        use_container_width=True,
    )


    # =====================================================
    # CRITIC EVALUATION
    # =====================================================

    ui_html(
        '<div class="section-heading">'
        '🧠 Critic Evaluation'
        '</div>'
    )

    with st.expander(
        "🔍 View Critic Agent Evaluation",
        expanded=False,
    ):

        st.markdown(report_evaluation)


    # =====================================================
    # SOURCE KNOWLEDGE
    # =====================================================

    ui_html(
        '<div class="section-heading">'
        '📚 Extracted Knowledge'
        '</div>'
    )

    with st.expander(
        "📖 View information extracted by Reader Agent",
        expanded=False,
    ):

        st.markdown(scraped_text)


    # =====================================================
    # RAW SEARCH RESULTS
    # =====================================================

    with st.expander(
        "🔎 View raw Search Agent results",
        expanded=False,
    ):

        st.markdown(search_text)


    # =====================================================
    # RESET RUN STATE
    # =====================================================

    st.session_state.run_research = False


# =========================================================
# EMPTY STATE
# =========================================================

else:

    ui_html(
        '<div class="empty-state">'
        '<div class="empty-icon">🧭</div>'
        '<div class="empty-title">'
        'Ready to investigate'
        '</div>'
        '<div class="empty-text">'
        'Enter a topic above and let the autonomous research '
        'pipeline do the heavy lifting.'
        '</div>'
        '</div>'
    )


# =========================================================
# FOOTER
# =========================================================

ui_html(
    '<div class="footer">'
    'Built with 🤖 multi-agent AI · LangChain · Streamlit'
    '</div>'
)