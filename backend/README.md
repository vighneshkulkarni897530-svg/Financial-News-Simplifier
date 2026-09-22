# FinNews AI — Backend Service

FastAPI-powered asynchronous backend providing financial news retrieval from NewsAPI, prompt-isolated inference via Groq LLaMA 3.3 70B, in-memory TTL caching, and robust schema validation.

---

## 🏗️ Architecture

```text
FastAPI Router (/api/news, /api/simplify, /health)
   │
   ├── NewsService (NewsAPI Ingestion, Deduplication, TTL Cache)
   ├── GroqService (LLaMA 3.3 70B Inference, Strict JSON parsing)
   └── SummarizationService (Concurrency control, text cleaning)
```

---

## 🚀 Getting Started

### 1. Requirements
* Python 3.11+
* NewsAPI Key ([newsapi.org](https://newsapi.org))
* Groq API Key ([console.groq.com](https://console.groq.com))

### 2. Installation
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Variables
Copy `.env.example` to `.env`:
```powershell
copy .env.example .env
```

Configure your API keys in `.env`:
```env
NEWS_API_KEY=your_newsapi_key
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
FRONTEND_ORIGIN=http://localhost:5500,http://127.0.0.1:5500
NEWS_CACHE_MINUTES=10
MAX_ARTICLE_LENGTH=12000
```

### 4. Running the Server
```powershell
uvicorn app.main:app --reload --port 8000
```
* **API Root**: `http://localhost:8000`
* **Swagger Documentation**: `http://localhost:8000/docs`
* **ReDoc**: `http://localhost:8000/redoc`

---

## 🧪 Testing

Run test suite with `pytest`:
```powershell
pytest tests -v
```
All unit and integration tests use comprehensive mocks and do not make live external API calls.
