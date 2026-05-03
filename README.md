# 🔍 FactLens · AI-Powered Fact Checker

> Upload any PDF — FactLens extracts verifiable claims and checks them against live web sources in seconds.

---

## What It Does

FactLens is a Streamlit web app that automatically fact-checks PDF documents using two AI APIs:

- **Groq (LLaMA 3.3 70B)** — extracts claims from your document and verdicts each one
- **Tavily Search** — searches the live web to find real evidence for each claim

Upload a PDF → get a verdict for every factual claim: ✓ Verified, ⚠ Inaccurate, ✗ False, or ? Unverified.

---

## Demo

| Step | What Happens |
|------|-------------|
| 1 | Upload a text-based PDF |
| 2 | LLaMA extracts up to 15 verifiable claims (stats, dates, figures, etc.) |
| 3 | Each claim is searched on the web via Tavily |
| 4 | LLaMA verdicts each claim with a source-backed explanation |
| 5 | View results by category + download a full JSON report |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| UI Framework | [Streamlit](https://streamlit.io/) |
| LLM | [Groq](https://groq.com/) — LLaMA 3.3 70B Versatile |
| Web Search | [Tavily](https://tavily.com/) — Advanced search with summaries |
| PDF Parsing | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io/) |

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/factlens.git
cd factlens
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set up API keys

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> **Get your keys:**
> - Groq: https://console.groq.com/keys (free tier available)
> - Tavily: https://app.tavily.com (free tier available)

### 4. Run the app

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Project Structure

```
factlens/
├── app.py              # Main application (single file)
├── requirements.txt    # Python dependencies
├── .env                # API keys (create this yourself, don't commit!)
└── README.md
```

---

## How It Works

```
PDF Upload
    │
    ▼
Extract Text (PyMuPDF)
    │
    ▼
Extract Claims (Groq LLaMA)
  └─ Finds up to 15 verifiable claims: stats, dates, figures, names
    │
    ▼
For each claim:
  ├─ Web Search (Tavily) → fetches 7 real sources
  └─ Verdict (Groq LLaMA) → VERIFIED / INACCURATE / FALSE / UNVERIFIED
    │
    ▼
Results Dashboard + JSON Export
```

---

## Verdict System

| Verdict | Meaning |
|---------|---------|
| ✓ **VERIFIED** | Web results clearly support the claim (including approximations) |
| ⚠ **INACCURATE** | Web results show a different specific figure or date |
| ✗ **FALSE** | Web results directly and strongly contradict the claim |
| ? **UNVERIFIED** | Results are unclear, mixed, or don't address the claim |

> The model is intentionally conservative — it picks **UNVERIFIED** over **FALSE** when evidence is ambiguous, to avoid false accusations.

---

## Requirements

```
streamlit>=1.35.0
PyMuPDF>=1.24.0
requests>=2.31.0
python-dotenv>=1.0.0
groq>=0.9.0
tavily-python>=0.3.0
```

---

## Limitations

- **Text-based PDFs only** — scanned or image-only PDFs won't work (no OCR)
- **Up to 15 claims per document** — configurable via `MAX_CLAIMS` in `app.py`
- **Accuracy depends on web coverage** — rare or niche claims may return UNVERIFIED due to limited search results
- **Not a substitute for human fact-checking** — always verify critical claims independently

---

## Configuration

You can tweak these constants at the top of `app.py`:

```python
GROQ_MODEL = "llama-3.3-70b-versatile"   # LLM model to use
MAX_CLAIMS = 15                            # Max claims to extract per document
```

---

## Deploying to Streamlit Cloud

1. Push your code to a public GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io) and connect your repo
3. Add your API keys under **Settings → Secrets**:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
TAVILY_API_KEY = "your_tavily_api_key_here"
```

---

## License

MIT License — free to use, modify, and distribute.

---

## Acknowledgements

Built with [Groq](https://groq.com/), [Tavily](https://tavily.com/), and [Streamlit](https://streamlit.io/).