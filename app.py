import streamlit as st
import json
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time
import uuid
from main import EnhancedResearchAgent
from tools import all_tools                      # YouTube tool removed from registry

# ─────────────────────────  PAGE CONFIG  ──────────────────────────
st.set_page_config(
    page_title="🧠 AI Research Assistant",
    page_icon="🧠",
    layout="wide"
)

# ───────────────────────────  GLOBAL CSS  ─────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700&display=swap');
    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
        background: radial-gradient(circle at top, #0F0F0F, #000000);
        color: white;
    }
    .main-header{font-size:2.5rem;font-weight:bold;text-align:center;margin-bottom:1.8rem;
                 background:linear-gradient(90deg,#BCFF4A 0%,#08F8E0 100%);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;}

    .stTextInput input,.stTextArea textarea{background:#111!important;color:#fff!important;
                                           border:1px solid #08F8E0;border-radius:8px;}
    .stButton>button{background:#BCFF4A;color:#000;font-weight:600;border-radius:8px;border:none;}
    .stButton>button:hover{background:#08F8E0;transform:translateY(-2px);
                           box-shadow:0 4px 12px rgba(8,248,224,.3);}
    h1,h2,h3{color:#BCFF4A;}
    .stProgress .st-bo{background:#08F8E0;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────  SESSION STATE  ────────────────────────
if "agent" not in st.session_state:
    st.session_state.agent = EnhancedResearchAgent()      # auto-init
if "history" not in st.session_state:
    st.session_state.history = []
if "latest" not in st.session_state:
    st.session_state.latest = None

# ───────────────────────────  HELPERS  ────────────────────────────
uid = lambda: str(uuid.uuid4())

def download_bundle(res: dict):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    c1,c2,c3 = st.columns(3)

    with c1:
        st.download_button(
            "⬇️ JSON", json.dumps(res, indent=2, ensure_ascii=False),
            f"research_{ts}.json","application/json",key=uid())

    with c2:
        txt = f"Title: {res['title']}\n\n{res['summary']}"
        st.download_button(
            "⬇️ TXT", txt, f"summary_{ts}.txt","text/plain",key=uid())

    with c3:
        rows = (
            [{"type":"finding","content":k} for k in res.get("key_findings",[])] +
            [{"type":"source","content":s} for s in res.get("sources",[])]
        )
        if rows:
            st.download_button(
                "⬇️ CSV", pd.DataFrame(rows).to_csv(index=False),
                f"data_{ts}.csv","text/csv",key=uid())

def render_result(res:dict, idx:int|None=None):
    st.subheader(f"📊 {res['title']}" if idx is None else f"📊 Research #{idx+1}: {res['title']}")
    m1,m2,m3 = st.columns(3)
    m1.metric("Confidence",f"{res.get('confidence_score',0):.2f}")
    m2.metric("Sources",len(res.get("sources",[])))
    m3.metric("Tools",len(res.get("tools_used",[])))

    st.write(res["summary"])
    if res.get("key_findings"):
        st.markdown("**Key Findings**")
        for k in res["key_findings"]:
            st.write(f"• {k}")
    if res.get("sources"):
        st.markdown("**Sources**")
        for s in res["sources"]:
            st.write(f"- {s}")
    st.markdown("**Tools:** "+", ".join(res.get("tools_used",[])))
    download_bundle(res)

# ───────────────────────────  HEADER  ─────────────────────────────
st.markdown('<h1 class="main-header">🧠 AI Research Assistant</h1>', unsafe_allow_html=True)

# Status bar
s1,s2,s3 = st.columns(3)
s1.success("🟢 Agent Ready")
s2.info(f"🛠️ {len(all_tools)} Tools")
s3.info(f"📊 {len(st.session_state.history)} Sessions")
st.markdown("---")

# ───────────────────────────  TABS  ───────────────────────────────
tab1, tab2, tab3 = st.tabs(["🔍 Research","📊 Results","📈 Analytics"])

# ░░░░░░░░░░░░░░░░░░░░  TAB 1 – RESEARCH  ░░░░░░░░░░░░░░░░░░░░
with tab1:
    st.header("🔍 Conduct Research")

    query = st.text_area(
        "Enter your research question or topic",
        placeholder="e.g. Latest developments in quantum computing",
        height=90,
    )

    save_flag = st.checkbox("💾 Save Results", value=True)
    # max_sources = st.slider("📚 Max Sources",3,15,8)
    # depth = st.selectbox("📈 Research Depth",["surface","moderate","comprehensive"])

    if st.button("🚀 Start Research", on_click=None, disabled= bool(query.strip())):
        with st.spinner("Conducting research…"):
            bar = st.progress(0)
            for p in (10,30,60,90):
                bar.progress(p); time.sleep(.3)

            try:
                res = st.session_state.agent.research(query, save_flag)
                st.session_state.latest = res
                st.session_state.history.insert(0,res)
                bar.progress(100)
                st.success("✅ Research complete!")
            except Exception as e:
                st.error(f"❌ {e}")

    if st.session_state.latest:
        st.markdown("---")
        render_result(st.session_state.latest)

# ░░░░░░░░░░░░░░░░░░░░  TAB 2 – RESULTS  ░░░░░░░░░░░░░░░░░░░░
with tab2:
    st.header("📊 Research Results History")
    if not st.session_state.history:
        st.info("No previous research sessions.")
    else:
        term = st.text_input("🔎 Filter by keyword")
        sort_by = st.selectbox("Sort by",["Latest","Confidence","Title"])
        filtered = [
            h for h in st.session_state.history
            if term.lower() in h["title"].lower() or term.lower() in h["summary"].lower()
        ] if term else st.session_state.history

        if sort_by=="Confidence":
            filtered.sort(key=lambda x:x.get("confidence_score",0), reverse=True)
        elif sort_by=="Title":
            filtered.sort(key=lambda x:x["title"])

        st.write(f"Showing {len(filtered)} of {len(st.session_state.history)} results")
        for i,h in enumerate(filtered):
            with st.expander(f"{h['title']}  —  {h.get('confidence_score',0):.2f}"):
                render_result(h,i)

# ░░░░░░░░░░░░░░░░░░░░  TAB 3 – ANALYTICS  ░░░░░░░░░░░░░░░░░░░
with tab3:
    st.header("📈 Session Analytics")
    if not st.session_state.history:
        st.info("Run research sessions to populate analytics.")
    else:
        df = pd.DataFrame([
            {"idx":i+1,
             "confidence":h["confidence_score"],
             "sources":len(h["sources"]),
             "tools":len(h["tools_used"])}
            for i,h in enumerate(st.session_state.history)
        ])
        c1,c2 = st.columns(2)
        c1.plotly_chart(px.line(df,x="idx",y="confidence",markers=True,
                                title="Confidence Over Sessions",
                                color_discrete_sequence=["#08F8E0"]),
                        use_container_width=True)
        c2.plotly_chart(px.bar(df,x="idx",y="sources",
                               title="Sources per Session",
                               color_discrete_sequence=["#BCFF4A"]),
                        use_container_width=True)
        st.metric("Average Confidence",f"{df['confidence'].mean():.2f}")
        st.metric("Avg. Sources",f"{df['sources'].mean():.1f}")


