
# 📈 FinNews AI — Financial News Simplification Platform

> **Transforming complex financial news and Wall Street jargon into crystal-clear, beginner-friendly explanations with Groq LLaMA 3.3 70B & FastAPI.**

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com)
[![Groq](https://img.shields.io/badge/AI_Engine-Groq_LLaMA_3.3_70B-purple.svg)](https://groq.com)
[![NewsAPI](https://img.shields.io/badge/News_Feed-NewsAPI-orange.svg)](https://newsapi.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📑 Table of Contents
1. [Overview & Problem Statement](#-overview--problem-statement)
2. [Product Principles](#-important-product-principles)
3. [Architecture & Data Flow](#-technical-architecture)
4. [Technology Stack](#-technology-stack)
5. [Directory Structure](#-directory-structure)
6. [Key Features](#-key-features)
7. [Environment Variables](#-environment-variables)
8. [Installation & Local Setup](#-installation--local-setup)
9. [API Documentation](#-api-endpoints)
10. [AI & Prompt Engineering](#-ai--prompt-engineering)
11. [News Ingestion, Caching & Deduplication](#-news-ingestion--caching)
12. [Security & Prompt Injection Defense](#-security--guardrails)
13. [Testing Suite](#-testing)
14. [Deployment Guide](#-deployment-guide)
15. [System & Functional Requirements](#-system-requirements)
16. [Troubleshooting](#-troubleshooting)
17. [Future Roadmap](#-future-roadmap)

---

## 🎯 Overview & Problem Statement

Financial and economic reporting is dense, full of confusing acronyms (e.g., *EBITDA, Basis Points, Quantitative Tightening, Yield Inversion*), and difficult for non-experts to digest. Retail investors, university students, and everyday consumers often struggle to understand how major economic announcements affect their personal finances.

**FinNews AI** bridges this knowledge gap by ingesting real-time global financial news and utilizing Groq's high-speed **LLaMA 3.3 70B Versatile** model to:
* Extract core facts and create 2-3 sentence summaries.
* Decode and explain complex financial terms in plain English.
* Provide balanced, objective context on why each story matters.
* Identify affected consumer and market groups without giving financial advice.

---

## ⚖️ Important Product Principles

FinNews AI is an **information simplification and educational platform**, NOT an automated financial or investment advisory tool.

* ❌ **The AI NEVER**: guarantees market profits, issues `BUY` or `SELL` directives, fabricates figures, or offers personalized portfolio management.
* ✅ **The AI ALWAYS**: maintains strict neutrality, uses objective language (*"The article reports that..."*), isolates third-party content against prompt injections, and clearly separates source facts from AI explanations.

---

## 🏗️ Technical Architecture

```text
                         ┌──────────────────────┐
                         │        USER          │
                         │   Desktop / Mobile   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │      FRONTEND        │
                         │  (HTML5 + CSS3 + JS) │
                         │ • News Dashboard     │
                         │ • Search & Filters   │
                         │ • Dynamic AI Cards   │
                         │ • Terms Glossary     │
                         └──────────┬───────────┘
                                    │
                               HTTP / REST
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FASTAPI BACKEND    │
                         │                      │
                         │ • Routes & Validation│
                         │ • Global Exception   │
                         │ • Sanitization       │
                         │ • TTL Cache Engine   │
                         └──────┬─────────┬─────┘
                                │         │
                                │         │
                                ▼         ▼
                      ┌─────────────┐ ┌──────────────┐
                      │   NewsAPI   │ │   Groq API   │
                      │             │ │              │
                      │ Live News   │ │ LLaMA 3.3    │
                      │ Ingestion   │ │ 70B Engine   │
                      └──────┬──────┘ └──────┬───────┘
                             │               │
                             └───────┬───────┘
                                     ▼
                           ┌─────────────────────┐
                           │ Processed Financial │
                           │ News + AI Summary   │
                           └──────────┬──────────┘
                                      │
                                      ▼
                             Frontend Display
```

---

## 💻 Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend** | Vanilla HTML5, CSS3, JavaScript ES6+ | High-performance, zero-dependency fintech UI |
| **Styling** | Custom Responsive CSS Design Tokens | Dark/Light theme, glassmorphism, micro-animations |
| **Backend** | Python 3.11+, FastAPI, Uvicorn | High-throughput asynchronous REST API |
| **Validation** | Pydantic v2 & Pydantic-Settings | Strict schema enforcement and type safety |
| **AI Inference** | Groq Cloud API (`llama-3.3-70b-versatile`) | Ultra-fast LLM reasoning and JSON simplification |
| **News Retrieval**| NewsAPI (`https://newsapi.org`) | Live global financial and market headlines |
| **HTTP Client** | `httpx` (async) | Async connection pooling, timeouts, and rate handling |
| **Testing** | `pytest`, `pytest-asyncio`, `pytest-mock` | Comprehensive unit and integration test suite |

---

## 📁 Directory Structure

```text
finnews-ai/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI entrypoint, CORS, exception handlers
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── health.py            # /health monitoring endpoint
│   │   │   ├── news.py              # /api/news and /api/news/search
│   │   │   └── simplify.py          # /api/simplify and /api/simplify/batch
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── news_service.py      # NewsAPI client, deduplication, TTL cache
│   │   │   ├── groq_service.py      # Groq LLaMA 3.3 70B integration & JSON parser
│   │   │   └── summarization_service.py # Coordination, cleaning, semaphore
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── news_schema.py       # Article, NewsResponse, ErrorResponse
│   │   │   └── summary_schema.py    # SimplificationResult, SimplifyRequest/Response
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py            # Pydantic BaseSettings and masked logging
│   │   │   └── logging_config.py    # Structured console logging
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── prompts.py           # Master system prompt and injection guardrails
│   │       └── text_cleaner.py      # HTML stripping, whitespace, length truncator
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py              # Pytest fixtures and mock payloads
│   │   ├── test_health.py           # Health and root router tests
│   │   ├── test_news.py             # NewsAPI, cache, deduplication tests
│   │   └── test_simplify.py         # Groq LLM parsing, validation, batch tests
│   ├── requirements.txt             # Python backend dependencies
│   ├── .env.example                 # Safe environment configuration template
│   └── README.md                    # Backend specific guide
├── frontend/
│   ├── index.html                   # Semantic HTML5 single-page application
│   ├── styles.css                   # Fintech design system & dark mode tokens
│   ├── app.js                       # Modular JavaScript ES6+ application logic
│   └── assets/                      # Static icons and assets
├── .gitignore                       # Ignored files (.env, venv, pycache, etc.)
├── README.md                        # Master project documentation
└── LICENSE                          # MIT License
```

---

## ✨ Key Features

1. **Live Financial News Stream**: Real-time articles categorized into *All, Markets, Economy, Business, Technology*.
2. **AI-Powered Simplification**: 2-3 sentence plain-English summary powered by LLaMA 3.3 70B.
3. **Financial Jargon Decoded**: Interactive chips that reveal clear explanations of terms like Inflation, Yield Curve, EPS, and Rate Hikes.
4. **Key Takeaways**: Instant bullet points capturing critical numbers, dates, and milestones.
5. **Objective Market Relevance**: Explains how policy or sector shifts might impact everyday borrowers and investors neutrally.
6. **Multi-Stage Loading State**: Informative skeleton animations indicating news ingestion and AI reasoning progress.
7. **Prompt Injection Guardrails**: Strict untrusted-content delimiters (`<<<UNTRUSTED_ARTICLE_CONTENT>>>`) prevent adversarial prompt exploits.
8. **In-Memory TTL Caching**: Eliminates duplicate NewsAPI and Groq requests.
9. **One-Click Batch Simplification**: Simplify top financial stories with a single click.
10. **Modern Dark/Light Mode**: Polished fintech aesthetics adhering to modern web design standards.

---

## 🔑 Environment Variables

Copy `backend/.env.example` to `backend/.env`:

```env
# NewsAPI Configuration (https://newsapi.org)
NEWS_API_KEY=your_newsapi_key_here

# Groq API Configuration (https://console.groq.com)
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Server Settings
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
ENVIRONMENT=development

# CORS Settings (comma-separated origins)
FRONTEND_ORIGIN=http://localhost:5500,http://127.0.0.1:5500

# Performance and Limits
NEWS_CACHE_MINUTES=10
MAX_ARTICLE_LENGTH=12000
```

> [!NOTE]
> Sensitive keys are masked on startup and are never exposed via endpoints or client scripts.

---

## 🚀 Installation & Local Setup

### 1. Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Launch FastAPI backend
uvicorn app.main:app --reload --port 8000
```

The backend starts at `http://localhost:8000`.

### 2. Frontend Setup

In a new terminal window:
```powershell
# Navigate to frontend directory
cd frontend

# Start local HTTP server
python -m http.server 5500
```

Open `http://localhost:5500` in your browser.

---

## 📡 API Endpoints

### 1. Root & Health Check
* `GET /`: Returns service metadata and operational status.
* `GET /health`: Returns service health status and configuration availability (`news_api_configured`, `groq_configured`).

### 2. Financial News
* `GET /api/news`:
  * Parameters: `category` (*all, markets, economy, business, technology*), `query`, `page`, `page_size`.
  * Response: Standard `NewsResponse` containing validated, deduplicated articles.
* `GET /api/news/search`:
  * Parameters: `query`, `page`, `page_size`.

### 3. AI Simplification
* `POST /api/simplify`:
  * Request Body:
    ```json
    {
      "title": "Fed Holds Benchmark Rate Steady at 5.25%",
      "description": "The Federal Reserve left interest rates unchanged...",
      "content": "Full article text...",
      "source": "Reuters",
      "url": "https://..."
    }
    ```
  * Response:
    ```json
    {
      "status": "success",
      "article": { "title": "...", "source": "..." },
      "simplification": {
        "simple_summary": "...",
        "key_points": ["..."],
        "financial_terms": [{ "term": "...", "explanation": "..." }],
        "why_it_matters": "...",
        "market_relevance": "...",
        "affected_groups": ["..."]
      }
    }
    ```
* `POST /api/simplify/batch`: Processes up to 10 articles concurrently with bounded concurrency.

---

## 🧠 AI & Prompt Engineering

Prompts are centralized in `backend/app/utils/prompts.py`.

### Safety & System Prompt Rules
1. Never invent facts, numbers, or sources.
2. Clearly distinguish article facts (*"The article reports that..."*) from contextual explanations.
3. Plain-English explanations suitable for high-school level comprehension.
4. Strictly forbidden from producing `BUY` / `SELL` advice or profit guarantees.
5. All untrusted publisher input is isolated:
   ```text
   <<<UNTRUSTED_ARTICLE_CONTENT>>>
   {article_text}
   <<<END_UNTRUSTED_ARTICLE_CONTENT>>>
   ```
6. Enforced structured JSON output matching Pydantic schemas.

---

## 📰 News Ingestion & Caching

* **Source**: NewsAPI (`https://newsapi.org/v2/everything`).
* **Deduplication Engine**: Evaluates canonical URL and normalized `title::source` strings to filter out syndicated reprints.
* **In-Memory TTL Cache**: Caches query results for `NEWS_CACHE_MINUTES` (default: 10 mins) to optimize API quota consumption.
* **Sanitization**: Strips HTML tags, script blocks, tracking URL parameters, and caps text at `MAX_ARTICLE_LENGTH`.

---

## 🛡️ Security & Guardrails

* **Secret Protection**: API keys are isolated in backend `.env` and never transferred to client browsers.
* **CORS Restrictions**: Configurable allowed origins via `FRONTEND_ORIGIN`.
* **Payload Length Limits**: Enforces input size caps to prevent denial-of-service and context overflow.
* **Sanitized Error Responses**: Internal stack traces are logged securely on the server and replaced with client-safe error codes (`NEWS_API_ERROR`, `GROQ_API_RATE_LIMIT`, `AI_RESPONSE_ERROR`, etc.).

---

## 🧪 Testing

The backend includes a comprehensive test suite in `backend/tests/`:

```powershell
python -m pytest backend/tests -v
```

### Test Coverage Highlights:
* `test_health.py`: Verifies `/` and `/health` configuration masking.
* `test_news.py`: Validates news parsing, in-memory caching, deduplication, rate limits, timeouts, and missing API key handling.
* `test_simplify.py`: Verifies Groq LLaMA JSON output, markdown fence stripping, short-payload rejection, rate limits, timeouts, malformed output recovery, and batch processing.

---

## 🌐 Deployment Guide

### Frontend Deployment (Vercel / Netlify / Cloudflare Pages)
* Deploy the `frontend/` folder to any static hosting provider.
* Configure the backend URL in `frontend/app.js` or via a global config:
  ```html
  <script>
    window.APP_CONFIG = { API_BASE_URL: "https://your-backend-api.onrender.com" };
  </script>
  ```

### Backend Deployment (Render / Railway / Google Cloud Run)
* Build container or Python environment using `backend/requirements.txt`.
* Start command:
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```
* Set production environment variables in your cloud dashboard (`NEWS_API_KEY`, `GROQ_API_KEY`, `FRONTEND_ORIGIN`).

---

## 📋 System Requirements

* **Operating System**: Windows, macOS, or Linux
* **Python**: Python 3.11 or higher
* **Memory**: 4 GB RAM minimum (8 GB recommended)
* **Browser**: Chrome, Firefox, Edge, or Safari (modern ES6+ support)

---

## 🔍 Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `MISSING_CONFIGURATION` | `NEWS_API_KEY` or `GROQ_API_KEY` missing in `.env` | Copy `.env.example` to `.env` and insert valid API keys. |
| `NEWS_API_RATE_LIMIT` | Exceeded NewsAPI 100 requests/day free tier | Wait for quota reset or adjust `NEWS_CACHE_MINUTES` to cache longer. |
| `GROQ_API_RATE_LIMIT` | Exceeded Groq requests per minute | The system will handle retries; wait a few moments before re-simplifying. |
| `Service Unavailable` badge | Backend is not running on port 8000 | Ensure Uvicorn is running: `uvicorn app.main:app --reload --port 8000`. |

---

## 🔮 Future Roadmap

* 👤 **User Profiles & Bookmarks**: Save preferred articles and create customized portfolios.
* 🌐 **Multilingual Simplification**: Hindi, Spanish, Marathi, French, and Japanese summaries.
* 🎙️ **Text-to-Speech (TTS)**: Listen to simplified financial briefings on the go.
* 💬 **AI Financial Chat**: Interactive Q&A regarding specific articles and economic reports.
* 📊 **Market Sentiment Indicators**: Visual sentiment gauge (Bullish / Neutral / Cautious).

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
