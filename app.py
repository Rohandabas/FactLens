import re
import time
import streamlit as st
import fitz
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from groq import Groq
from tavily import TavilyClient

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactLens · AI Fact-Checker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:ital,wght@0,400;0,500;1,400&family=Lora:ital,wght@0,400;0,600;1,400&display=swap');
  :root {
    --ink:#0d0d0d;--paper:#f5f0e8;--cream:#ede8dc;
    --rust:#c0392b;--gold:#d4a017;--forest:#2d6a4f;
    --slate:#4a5568;--border:#c8bfaa;--blue:#1a73e8;
  }
  html,body,[class*="css"]{font-family:'Lora',Georgia,serif;background:var(--paper);color:var(--ink);}
  #MainMenu,footer,header{visibility:hidden;}
  .block-container{padding:2rem 3rem 4rem;max-width:1100px;}
  .masthead{border-top:4px solid var(--ink);border-bottom:2px solid var(--ink);padding:1.4rem 0 1rem;margin-bottom:2.5rem;display:flex;align-items:baseline;gap:1.2rem;flex-wrap:wrap;}
  .masthead-title{font-family:'Syne',sans-serif;font-weight:800;font-size:2.6rem;letter-spacing:-1px;line-height:1;color:#ffffff !important;}
  .masthead-sub{font-family:'DM Mono',monospace;font-size:0.72rem;letter-spacing:0.15em;color:var(--slate);text-transform:uppercase;border-left:2px solid var(--border);padding-left:1rem;}
  .edition-tag{margin-left:auto;font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:0.1em;color:var(--slate);text-transform:uppercase;}
  .claim-card{border:1px solid var(--border);border-radius:2px;background:#fff;padding:1.4rem 1.6rem;margin-bottom:1.2rem;position:relative;overflow:hidden;}
  .claim-card::before{content:'';position:absolute;left:0;top:0;bottom:0;width:5px;}
  .card-verified::before{background:var(--forest);}
  .card-inaccurate::before{background:var(--gold);}
  .card-false::before{background:var(--rust);}
  .card-unverified::before{background:var(--slate);}
  .verdict-badge{display:inline-block;font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;padding:0.22rem 0.65rem;border-radius:1px;font-weight:500;margin-bottom:0.8rem;}
  .badge-verified{background:#d4edda;color:var(--forest);border:1px solid var(--forest);}
  .badge-inaccurate{background:#fff3cd;color:#7d5a00;border:1px solid var(--gold);}
  .badge-false{background:#fde8e8;color:var(--rust);border:1px solid var(--rust);}
  .badge-unverified{background:#e9ecef;color:var(--slate);border:1px solid #adb5bd;}
  .claim-text{font-family:'Lora',serif;font-style:italic;font-size:1.02rem;line-height:1.6;margin-bottom:0.9rem;color:var(--ink);}
  .analysis-label{font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:0.12em;text-transform:uppercase;color:var(--slate);margin-bottom:0.3rem;}
  .analysis-body{font-size:0.92rem;line-height:1.65;color:#333;}
  .source-chip{display:inline-block;font-family:'DM Mono',monospace;font-size:0.68rem;color:var(--blue);background:#e8f0fe;border:1px solid #c5d8fb;border-radius:2px;padding:0.15rem 0.5rem;margin:0.4rem 0.3rem 0 0;word-break:break-all;}
  .scoreboard{display:flex;gap:1.2rem;margin-bottom:2.5rem;flex-wrap:wrap;}
  .score-box{flex:1;min-width:120px;border:1px solid var(--border);background:#fff;padding:1rem 1.2rem;text-align:center;border-radius:2px;}
  .score-number{font-family:'Syne',sans-serif;font-weight:800;font-size:2.4rem;line-height:1;}
  .score-label{font-family:'DM Mono',monospace;font-size:0.65rem;letter-spacing:0.1em;text-transform:uppercase;color:var(--slate);margin-top:0.25rem;}
  .num-verified{color:var(--forest);}.num-inaccurate{color:#7d5a00;}.num-false{color:var(--rust);}.num-unverified{color:var(--slate);}
  .section-heading{font-family:'Syne',sans-serif;font-weight:700;font-size:1.15rem;letter-spacing:-0.02em;border-bottom:1px solid var(--border);padding-bottom:0.5rem;margin:2rem 0 1.2rem;color:var(--ink);}
  .stButton>button{font-family:'Syne',sans-serif;font-weight:700;font-size:0.9rem;letter-spacing:0.05em;background:var(--ink);color:var(--paper);border:none;border-radius:2px;padding:0.65rem 2rem;width:100%;}
  .stButton>button:hover{background:#2d2d2d;}
  .stProgress>div>div>div{background:var(--ink);}
  [data-testid="stFileUploader"]{background:var(--cream);border:1px dashed var(--border);border-radius:2px;padding:0.5rem;}
  .info-strip{background:var(--cream);border:1px solid var(--border);border-radius:2px;padding:0.8rem 1.2rem;font-family:'DM Mono',monospace;font-size:0.78rem;color:var(--slate);margin-bottom:1.2rem;}
  .correct-box{margin-top:0.9rem;padding:0.7rem 1rem;background:#f8f4ec;border-left:3px solid #c8bfaa;}
  .free-badge{background:#d4edda;border:1px solid var(--forest);border-radius:2px;padding:0.8rem 1.2rem;font-family:'DM Mono',monospace;font-size:0.75rem;color:var(--forest);margin-bottom:1.5rem;}
</style>
""", unsafe_allow_html=True)


# ── Config ─────────────────────────────────────────────────────────────────────
GROQ_MODEL = "llama-3.3-70b-versatile"
MAX_CLAIMS = 15


# ── API Keys ───────────────────────────────────────────────────────────────────
def get_secret(key: str) -> str:
    val = os.getenv(key, "")
    if val:
        return val
    try:
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        return ""

groq_key   = get_secret("GROQ_API_KEY")
tavily_key = get_secret("TAVILY_API_KEY")

if not groq_key:
    st.error("⚠️ GROQ_API_KEY not found. Add it to .env (local) or Streamlit Secrets (cloud).")
    st.stop()
if not tavily_key:
    st.error("⚠️ TAVILY_API_KEY not found. Add it to .env (local) or Streamlit Secrets (cloud).")
    st.stop()

groq_client   = Groq(api_key=groq_key)
tavily_client = TavilyClient(api_key=tavily_key)


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_pdf_text(uploaded_file) -> str:
    data = uploaded_file.read()
    doc  = fitz.open(stream=data, filetype="pdf")
    return "\n\n".join(page.get_text() for page in doc)


def clean_json(raw: str) -> str:
    raw = raw.strip()
    if "```" in raw:
        parts = raw.split("```")
        for part in parts:
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("[") or part.startswith("{"):
                raw = part
                break
    start = raw.find("[")
    end   = raw.rfind("]") + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    return raw.strip()


def extract_claims(text: str) -> list:
    """Use Groq to extract verifiable claims from document text."""
    doc_text = text[:8000]

    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        temperature=0.0,
        max_tokens=3000,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a fact-extraction expert. "
                    "Return ONLY valid JSON arrays. No markdown, no backticks, no explanation whatsoever."
                ),
            },
            {
                "role": "user",
                "content": f"""Extract up to {MAX_CLAIMS} specific, verifiable claims from this document.

Focus on claims that contain:
- Specific numbers, statistics, percentages
- Specific dates or time periods
- Named companies, people, products with attributed facts
- Financial figures or market data
- Scientific or research findings

Skip vague or opinion-based statements.

Each item must have exactly these 3 fields:
{{"id": 1, "claim": "exact claim text", "category": "statistic"}}

Category must be one of: statistic | date | financial | technical | research | demographic | scientific | other

DOCUMENT:
{doc_text}

JSON array:""",
            },
        ],
    )

    raw = clean_json(response.choices[0].message.content)
    raw = re.sub(r",\s*\]", "]", raw)
    raw = re.sub(r",\s*\}", "}", raw)

    try:
        return json.loads(raw)[:MAX_CLAIMS]
    except json.JSONDecodeError:
        last_good = raw.rfind("},")
        if last_good == -1:
            last_good = raw.rfind("}")
        if last_good != -1:
            raw = raw[:last_good + 1] + "]"
            raw = re.sub(r",\s*\]", "]", raw)
            try:
                return json.loads(raw)[:MAX_CLAIMS]
            except Exception:
                pass
        return []


def search_web(claim: str) -> tuple:
    """
    Search using the raw claim text directly.
    Uses advanced depth and more results to reduce hallucination.
    """
    try:
        result = tavily_client.search(
            query=claim,                  # raw claim = better factual hits
            search_depth="advanced",      # deeper search than "basic"
            max_results=7,                # more sources = less hallucination
            include_answer=True,
            include_raw_content=False,
        )

        context_parts = []
        if result.get("answer"):
            context_parts.append(f"Web summary: {result['answer']}")

        sources = []
        for r in result.get("results", []):
            title   = r.get("title", "")
            content = r.get("content", "")[:400]
            url     = r.get("url", "")
            context_parts.append(f"- [{title}]: {content}")
            if url:
                sources.append({"title": title or url, "uri": url})

        return "\n".join(context_parts)[:3000], sources

    except Exception as e:
        return f"Search failed: {e}", []


def verify_claim(claim: dict) -> dict:
    """
    Search web with Tavily, then ask Groq to verdict the claim.
    Improved prompt with strict rules against hallucination and over-labeling.
    """
    web_context, sources = search_web(claim["claim"])

    prompt = f"""You are a careful, nuanced fact-checker. Verify the claim using ONLY the web search results provided below. Do NOT use your training knowledge to invent corrections or figures.

CLAIM: "{claim['claim']}"
Category: {claim['category']}

WEB SEARCH RESULTS:
{web_context}

VERDICT RULES — read carefully:
- VERIFIED   → search results clearly support the claim, including reasonable approximations (e.g. "~95%", "about $4 trillion", "roughly 2.5 billion" all count as verified if directionally correct)
- INACCURATE → search results show a clearly DIFFERENT specific number or date — you must cite the exact correct figure from the results
- FALSE      → search results directly and strongly contradict the claim with solid evidence
- UNVERIFIED → search results are unclear, mixed, contradictory, or don't directly address the claim

CRITICAL RULES YOU MUST FOLLOW:
1. If results are ambiguous or show a range → use UNVERIFIED, never guess
2. Approximations and rounded figures count as VERIFIED if directionally correct
3. Only fill "correct_info" if search results give a CLEAR specific correction — otherwise leave it as an empty string
4. Do NOT confuse related but different entities (e.g. "Meta AI users" is NOT the same as "Facebook monthly active users"; "Google Search share" is NOT the same as "Google overall revenue share")
5. When in doubt between FALSE and UNVERIFIED → choose UNVERIFIED
6. Your explanation must cite specific data points from the search results — never make up numbers

Reply ONLY with a JSON object. No markdown, no backticks, nothing else:
{{
  "verdict": "VERIFIED|INACCURATE|FALSE|UNVERIFIED",
  "confidence": "high|medium|low",
  "explanation": "2-3 sentences. Must cite specific data from search results. Do not invent any numbers.",
  "correct_info": "Only fill if search results give a clear specific correction. Otherwise empty string."
}}"""

    try:
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            temperature=0.0,       # zero temperature = no hallucination
            max_tokens=600,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a precise, conservative fact-checker. "
                        "You only use information from the provided search results. "
                        "You never invent corrections, figures, or statistics. "
                        "When uncertain, you always choose UNVERIFIED over FALSE. "
                        "You never confuse related but distinct entities or products."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        )

        raw = response.choices[0].message.content.strip()
        raw = re.sub(r"```json|```", "", raw).strip()
        start = raw.find("{")
        end   = raw.rfind("}") + 1
        if start != -1 and end > start:
            data = json.loads(raw[start:end])
            return {**claim, **data, "sources": sources}

    except Exception as e:
        return {
            **claim,
            "verdict":      "UNVERIFIED",
            "confidence":   "low",
            "explanation":  f"Verification error: {str(e)[:150]}",
            "correct_info": "",
            "sources":      sources,
        }

    return {
        **claim,
        "verdict":      "UNVERIFIED",
        "confidence":   "low",
        "explanation":  "Could not parse model response.",
        "correct_info": "",
        "sources":      sources,
    }


def render_claim_card(result: dict):
    verdict     = result.get("verdict", "UNVERIFIED").upper()
    card_class  = {"VERIFIED":"card-verified","INACCURATE":"card-inaccurate","FALSE":"card-false"}.get(verdict, "card-unverified")
    badge_class = {"VERIFIED":"badge-verified","INACCURATE":"badge-inaccurate","FALSE":"badge-false"}.get(verdict, "badge-unverified")
    icon        = {"VERIFIED":"✓","INACCURATE":"⚠","FALSE":"✗","UNVERIFIED":"?"}[verdict]
    confidence  = result.get("confidence", "")
    conf_html   = f' <span style="font-size:0.6rem;opacity:0.7;">({confidence} confidence)</span>' if confidence else ""

    correct_html = ""
    if result.get("correct_info"):
        correct_html = f'''<div class="correct-box">
          <div class="analysis-label">Correct / Current Information</div>
          <div class="analysis-body">{result["correct_info"]}</div>
        </div>'''

    sources_html = ""
    srcs = result.get("sources", [])
    if srcs:
        chips = "".join(
            f'<a class="source-chip" href="{s["uri"]}" target="_blank">🔗 {s["title"][:55]}</a>'
            for s in srcs[:4]
        )
        sources_html = f'<div style="margin-top:0.7rem;"><div class="analysis-label">Sources (Web Search)</div>{chips}</div>'

    st.markdown(f"""
    <div class="claim-card {card_class}">
      <span class="verdict-badge {badge_class}">{icon} {verdict}{conf_html}</span>
      <div class="claim-text">{result['claim']}</div>
      <div class="analysis-label">Verification Analysis</div>
      <div class="analysis-body">{result.get('explanation', '')}</div>
      {correct_html}
      {sources_html}
    </div>""", unsafe_allow_html=True)


# ── Layout ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="masthead">
  <div class="masthead-title">FactLens</div>  
  <div class="masthead-sub">AI-Powered Claim Verification</div>
 <div class="masthead-sub">MAX_CLAIMS = 15</div>
  <div class="edition-tag">Groq LLaMA 3.3 70B + Tavily Search &nbsp;·&nbsp; {datetime.now().strftime('%d %b %Y')}</div>
</div>
""", unsafe_allow_html=True)



st.markdown('<div class="section-heading">Upload Document</div>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "Drop a PDF here",
    type=["pdf"],
    help="Supports text-based PDFs. Scanned/image PDFs won't work.",
    label_visibility="collapsed",
)

if uploaded:
    st.markdown(
        f'<div class="info-strip">📄 <strong>{uploaded.name}</strong> — {uploaded.size:,} bytes</div>',
        unsafe_allow_html=True,
    )

run_btn = st.button("🔍 Run Fact-Check", disabled=(not uploaded))


# ── Processing ─────────────────────────────────────────────────────────────────
if run_btn and uploaded:

    # Step 0: Extract PDF text
    with st.spinner("Reading PDF…"):
        pdf_text = extract_pdf_text(uploaded)
        if len(pdf_text.strip()) < 50:
            st.error("Could not extract text. The PDF may be image-only or scanned.")
            st.stop()

    with st.expander("📄 Extracted text (preview)", expanded=False):
        st.text_area(
            "", pdf_text[:3000] + ("…" if len(pdf_text) > 3000 else ""),
            height=180, label_visibility="collapsed",
        )

    # Step 1: Extract claims
    st.markdown('<div class="section-heading">Step 1 · Extracting Claims</div>', unsafe_allow_html=True)
    with st.spinner("Identifying verifiable claims with Groq LLaMA…"):
        try:
            claims = extract_claims(pdf_text)
        except Exception as e:
            st.error(f"Claim extraction failed: {e}")
            st.stop()

    if not claims:
        st.error("No claims could be extracted. Try a PDF with more factual/statistical content.")
        st.stop()

    st.success(f"Found **{len(claims)}** verifiable claims — verifying against live web…")

    # Step 2: Verify claims sequentially
    st.markdown(
        '<div class="section-heading">Step 2 · Verifying Against Live Web (Tavily Search)</div>',
        unsafe_allow_html=True,
    )

    progress_bar = st.progress(0)
    status_text  = st.empty()
    results      = []

    for i, claim in enumerate(claims):
        short = claim["claim"][:85] + ("…" if len(claim["claim"]) > 85 else "")
        status_text.markdown(
            f'<div class="info-strip">🔍 Verifying {i+1}/{len(claims)}: <em>{short}</em></div>',
            unsafe_allow_html=True,
        )
        try:
            result = verify_claim(claim)
        except Exception as e:
            result = {
                **claim,
                "verdict":      "UNVERIFIED",
                "confidence":   "low",
                "explanation":  str(e)[:200],
                "correct_info": "",
                "sources":      [],
            }
        results.append(result)
        progress_bar.progress((i + 1) / len(claims))
        time.sleep(0.3)  # small courtesy delay

    status_text.empty()

    # ── Scoreboard ──────────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">Results Summary</div>', unsafe_allow_html=True)
    counts = {
        v: sum(1 for r in results if r.get("verdict") == v)
        for v in ["VERIFIED", "INACCURATE", "FALSE", "UNVERIFIED"]
    }
    total    = len(results)
    accuracy = int((counts["VERIFIED"] / total) * 100) if total else 0

    st.markdown(f"""
    <div class="scoreboard">
      <div class="score-box"><div class="score-number num-verified">{counts['VERIFIED']}</div><div class="score-label">Verified</div></div>
      <div class="score-box"><div class="score-number num-inaccurate">{counts['INACCURATE']}</div><div class="score-label">Inaccurate</div></div>
      <div class="score-box"><div class="score-number num-false">{counts['FALSE']}</div><div class="score-label">False</div></div>
      <div class="score-box"><div class="score-number num-unverified">{counts['UNVERIFIED']}</div><div class="score-label">Unverified</div></div>
      <div class="score-box"><div class="score-number" style="color:var(--ink);">{accuracy}%</div><div class="score-label">Accuracy Rate</div></div>
    </div>""", unsafe_allow_html=True)

    # ── Tabbed results ──────────────────────────────────────────────────────────
    tab_all, tab_v, tab_i, tab_f, tab_u = st.tabs([
        f"All ({total})",
        f"✓ Verified ({counts['VERIFIED']})",
        f"⚠ Inaccurate ({counts['INACCURATE']})",
        f"✗ False ({counts['FALSE']})",
        f"? Unverified ({counts['UNVERIFIED']})",
    ])

    for tab, fv in [
        (tab_all, None), (tab_v, "VERIFIED"), (tab_i, "INACCURATE"),
        (tab_f, "FALSE"), (tab_u, "UNVERIFIED"),
    ]:
        with tab:
            filtered = [r for r in results if fv is None or r.get("verdict") == fv]
            if not filtered:
                st.markdown('<div class="info-strip">No claims in this category.</div>', unsafe_allow_html=True)
            for r in filtered:
                render_claim_card(r)

    # ── Export ──────────────────────────────────────────────────────────────────
    st.markdown('<div class="section-heading">Export</div>', unsafe_allow_html=True)
    export = {
        "document":      uploaded.name,
        "model":         GROQ_MODEL,
        "checked_at":    datetime.now().isoformat(),
        "summary":       counts,
        "accuracy_rate": f"{accuracy}%",
        "results":       results,
    }
    st.download_button(
        "⬇ Download Full Report (JSON)",
        data=json.dumps(export, indent=2),
        file_name=f"factcheck_{uploaded.name.replace('.pdf', '')}.json",
        mime="application/json",
    )

elif not uploaded:
    st.markdown("""
    <div style="text-align:center;padding:3rem 0;color:#aaa;
                font-family:'DM Mono',monospace;font-size:0.8rem;letter-spacing:0.08em;">
      ↑ UPLOAD A PDF TO BEGIN VERIFICATION
    </div>""", unsafe_allow_html=True)