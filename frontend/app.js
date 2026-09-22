/**
 * FinNews AI — Frontend Application Logic
 * Modular vanilla JavaScript ES6+ architecture
 */

// Configuration: unified API Base URL
const API_BASE_URL = window.APP_CONFIG?.API_BASE_URL || "http://localhost:8000";

// Global App State
const state = {
  currentCategory: "all",
  currentQuery: "",
  articles: [],
  simplifiedMap: new Map(), // articleUrl -> simplificationResult
  isLoading: false,
  isBatchSimplifying: false,
  isOnline: false,
  loadingInterval: null,
};

// DOM Elements
const elements = {
  healthBadge: document.getElementById("healthBadge"),
  healthStatusText: document.getElementById("healthStatusText"),
  themeToggleBtn: document.getElementById("themeToggleBtn"),
  mobileMenuBtn: document.getElementById("mobileMenuBtn"),
  mobileNavDrawer: document.getElementById("mobileNavDrawer"),
  categoryPills: document.querySelectorAll(".category-pill"),
  searchForm: document.getElementById("searchForm"),
  searchInput: document.getElementById("searchInput"),
  clearSearchBtn: document.getElementById("clearSearchBtn"),
  resultsInfoBar: document.getElementById("resultsInfoBar"),
  resultsCountText: document.getElementById("resultsCountText"),
  refreshFeedBtn: document.getElementById("refreshFeedBtn"),
  heroFetchBtn: document.getElementById("heroFetchBtn"),
  fetchAndSimplifyAllBtn: document.getElementById("fetchAndSimplifyAllBtn"),
  newsGrid: document.getElementById("newsGrid"),
  loadingState: document.getElementById("loadingState"),
  errorState: document.getElementById("errorState"),
  errorCodeBadge: document.getElementById("errorCodeBadge"),
  errorTitle: document.getElementById("errorTitle"),
  errorMessage: document.getElementById("errorMessage"),
  retryBtn: document.getElementById("retryBtn"),
  loadDemoBtn: document.getElementById("loadDemoBtn"),
  emptyState: document.getElementById("emptyState"),
  resetFiltersBtn: document.getElementById("resetFiltersBtn"),
  toastContainer: document.getElementById("toastContainer"),
};

// ==============================================================================
// 1. Initial Application Setup & Theme Handling
// ==============================================================================

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  initEventListeners();
  checkHealth();
  // Fetch initial news feed
  fetchNews({ category: "all" });
});

function initTheme() {
  const savedTheme = localStorage.getItem("finnews_theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
  const newTheme = currentTheme === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("finnews_theme", newTheme);
}

// ==============================================================================
// 2. Event Listeners
// ==============================================================================

function initEventListeners() {
  // Theme toggle
  elements.themeToggleBtn.addEventListener("click", toggleTheme);

  // Mobile navigation drawer toggle
  elements.mobileMenuBtn.addEventListener("click", () => {
    elements.mobileNavDrawer.classList.toggle("open");
  });

  // Category filter tabs
  elements.categoryPills.forEach((pill) => {
    pill.addEventListener("click", (e) => {
      const category = pill.getAttribute("data-category");
      if (category === state.currentCategory && !state.currentQuery) return;

      elements.categoryPills.forEach((p) => {
        p.classList.remove("active");
        p.setAttribute("aria-selected", "false");
      });
      pill.classList.add("active");
      pill.setAttribute("aria-selected", "true");

      state.currentCategory = category;
      state.currentQuery = "";
      elements.searchInput.value = "";
      elements.clearSearchBtn.style.display = "none";

      fetchNews({ category: state.currentCategory });
    });
  });

  // Search submission
  elements.searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const query = elements.searchInput.value.trim();
    if (!query) return;

    state.currentQuery = query;
    // Reset category tabs visual
    elements.categoryPills.forEach((p) => {
      p.classList.remove("active");
      p.setAttribute("aria-selected", "false");
    });

    fetchNews({ query: state.currentQuery });
  });

  // Search input change / clear
  elements.searchInput.addEventListener("input", (e) => {
    if (e.target.value.trim().length > 0) {
      elements.clearSearchBtn.style.display = "block";
    } else {
      elements.clearSearchBtn.style.display = "none";
    }
  });

  elements.clearSearchBtn.addEventListener("click", () => {
    elements.searchInput.value = "";
    elements.clearSearchBtn.style.display = "none";
    state.currentQuery = "";
    // Reset to current category
    const activePill = document.querySelector(`.category-pill[data-category="${state.currentCategory}"]`);
    if (activePill) {
      activePill.classList.add("active");
      activePill.setAttribute("aria-selected", "true");
    }
    fetchNews({ category: state.currentCategory });
  });

  // Refresh feed button
  elements.refreshFeedBtn.addEventListener("click", () => {
    fetchNews({ category: state.currentCategory, query: state.currentQuery });
  });

  // Hero section CTAs
  elements.heroFetchBtn.addEventListener("click", () => {
    const dashboard = document.getElementById("dashboard");
    if (dashboard) dashboard.scrollIntoView({ behavior: "smooth" });
    fetchAndSimplifyTopArticles();
  });

  // Fetch & Simplify All Button
  elements.fetchAndSimplifyAllBtn.addEventListener("click", () => {
    fetchAndSimplifyTopArticles();
  });

  // Error retry button
  elements.retryBtn.addEventListener("click", () => {
    fetchNews({ category: state.currentCategory, query: state.currentQuery });
  });

  // Load demo articles button
  if (elements.loadDemoBtn) {
    elements.loadDemoBtn.addEventListener("click", () => {
      loadDemoArticles();
    });
  }

  // Reset filters empty state button
  elements.resetFiltersBtn.addEventListener("click", () => {
    state.currentCategory = "all";
    state.currentQuery = "";
    elements.searchInput.value = "";
    elements.clearSearchBtn.style.display = "none";
    elements.categoryPills.forEach((p) => {
      const isAll = p.getAttribute("data-category") === "all";
      p.classList.toggle("active", isAll);
      p.setAttribute("aria-selected", isAll ? "true" : "false");
    });
    fetchNews({ category: "all" });
  });
}

// ==============================================================================
// 3. Health Monitoring
// ==============================================================================

async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);
    if (!response.ok) throw new Error("Health check failed");
    const data = await response.json();

    if (data.status === "healthy" && data.news_api_configured && data.groq_configured) {
      state.isOnline = true;
      elements.healthBadge.className = "health-badge online";
      elements.healthStatusText.textContent = "AI Online";
      elements.healthBadge.title = "NewsAPI and Groq LLaMA 3.3 70B operational";
    } else if (data.status === "healthy") {
      state.isOnline = true;
      elements.healthBadge.className = "health-badge";
      elements.healthStatusText.textContent = "API Ready (Keys Pending)";
      elements.healthBadge.title = "Backend is running. API keys configuration needed for live requests.";
    }
  } catch (err) {
    state.isOnline = false;
    elements.healthBadge.className = "health-badge offline";
    elements.healthStatusText.textContent = "Service Unavailable";
    elements.healthBadge.title = "Could not connect to FastAPI backend at " + API_BASE_URL;
  }
}

// ==============================================================================
// 4. News Retrieval & Multi-Stage Loading
// ==============================================================================

async function fetchNews({ category = "all", query = "", page = 1, page_size = 9 } = {}) {
  showLoading(1);
  hideError();
  hideEmpty();
  elements.newsGrid.innerHTML = "";

  const params = new URLSearchParams();
  if (query) {
    params.append("query", query);
  } else if (category) {
    params.append("category", category);
  }
  params.append("page", page.toString());
  params.append("page_size", page_size.toString());

  try {
    const response = await fetch(`${API_BASE_URL}/api/news?${params.toString()}`);
    const data = await response.json();

    if (!response.ok) {
      const errCode = data.code || `HTTP_${response.status}`;
      const errMsg = data.message || "Failed to retrieve financial news.";
      throw { code: errCode, message: errMsg };
    }

    state.articles = data.articles || [];
    hideLoading();

    if (state.articles.length === 0) {
      showEmpty();
      elements.resultsCountText.textContent = "0 articles found";
    } else {
      elements.resultsCountText.textContent = `Showing ${state.articles.length} financial articles ${query ? `for "${query}"` : `in ${category}`}`;
      renderNews(state.articles);
    }
  } catch (error) {
    hideLoading();
    showError(error.code || "CONNECTION_ERROR", error.message || "Unable to reach FinNews AI backend service.");
  }
}

function showLoading(initialStage = 1) {
  state.isLoading = true;
  elements.loadingState.style.display = "flex";
  elements.resultsInfoBar.style.display = "none";
  elements.newsGrid.style.display = "none";

  // Cycle stage progress
  let currentStage = initialStage;
  updateLoadingStageUI(currentStage);

  if (state.loadingInterval) clearInterval(state.loadingInterval);
  state.loadingInterval = setInterval(() => {
    currentStage = currentStage < 3 ? currentStage + 1 : 1;
    updateLoadingStageUI(currentStage);
  }, 1800);
}

function updateLoadingStageUI(stageNum) {
  for (let i = 1; i <= 3; i++) {
    const stageEl = document.getElementById(`stage${i}`);
    if (stageEl) {
      stageEl.classList.toggle("active", i === stageNum);
    }
  }
}

function hideLoading() {
  state.isLoading = false;
  if (state.loadingInterval) clearInterval(state.loadingInterval);
  elements.loadingState.style.display = "none";
  elements.resultsInfoBar.style.display = "flex";
  elements.newsGrid.style.display = "grid";
}

function showError(code, message) {
  elements.errorCodeBadge.textContent = code;
  elements.errorMessage.textContent = message;
  elements.errorState.style.display = "block";
  elements.resultsInfoBar.style.display = "none";
  elements.newsGrid.style.display = "none";
}

function hideError() {
  elements.errorState.style.display = "none";
}

function showEmpty() {
  elements.emptyState.style.display = "block";
  elements.newsGrid.style.display = "none";
}

function hideEmpty() {
  elements.emptyState.style.display = "none";
}

// ==============================================================================
// 5. News Rendering & Card Components
// ==============================================================================

function renderNews(articles) {
  elements.newsGrid.innerHTML = "";

  articles.forEach((article, index) => {
    const card = createNewsCardElement(article, index);
    elements.newsGrid.appendChild(card);
  });
}

function createNewsCardElement(article, index) {
  const card = document.createElement("article");
  card.className = "news-card";
  card.id = `newsCard_${index}`;

  const timeFormatted = formatRelativeTime(article.published_at);
  const isSimplified = state.simplifiedMap.has(article.url);

  card.innerHTML = `
    <div class="card-media-wrapper">
      ${
        article.image_url
          ? `<img src="${escapeHtml(article.image_url)}" alt="${escapeHtml(article.title)}" class="card-img" loading="lazy" onerror="this.onerror=null;this.parentElement.innerHTML='<div class=\\'img-fallback-placeholder\\'>📈</div>';">`
          : `<div class="img-fallback-placeholder">📈</div>`
      }
      <span class="card-source-tag">${escapeHtml(article.source || "News")}</span>
    </div>

    <div class="card-body">
      <div class="card-meta">
        <span class="card-time">${timeFormatted}</span>
      </div>

      <h3 class="card-title">${escapeHtml(article.title)}</h3>
      <p class="card-desc">${escapeHtml(article.description || article.content || "Click 'Simplify with AI' to analyze and explain this report.")}</p>

      <!-- AI Simplification Container Target -->
      <div class="ai-container-slot" id="aiSlot_${index}"></div>

      <div class="card-actions">
        <button class="simplify-btn" id="simplifyBtn_${index}">
          <span class="btn-sparkle">✨</span>
          <span class="btn-label">${isSimplified ? "Re-Simplify" : "Simplify with AI"}</span>
        </button>
        <a href="${escapeHtml(article.url)}" target="_blank" rel="noopener noreferrer" class="read-orig-link">
          Read Original ↗
        </a>
      </div>
    </div>
  `;

  // Attach Simplify Button Event
  const simplifyBtn = card.querySelector(`#simplifyBtn_${index}`);
  simplifyBtn.addEventListener("click", () => {
    simplifyArticle(article, index, card);
  });

  // If already simplified in state, render it immediately
  if (isSimplified) {
    const cachedResult = state.simplifiedMap.get(article.url);
    renderSummaryToCard(index, cachedResult);
  }

  return card;
}

// ==============================================================================
// 6. AI Simplification Flow
// ==============================================================================

async function simplifyArticle(article, index, cardElement) {
  const simplifyBtn = cardElement.querySelector(`#simplifyBtn_${index}`);
  const aiSlot = cardElement.querySelector(`#aiSlot_${index}`);
  if (!simplifyBtn || !aiSlot) return;

  // Set loading state on button
  simplifyBtn.disabled = true;
  simplifyBtn.innerHTML = `<span class="spinner-ring" style="width:14px;height:14px;border-width:2px;"></span> Analyzing...`;

  aiSlot.innerHTML = `
    <div class="ai-simplified-container" style="opacity: 0.85;">
      <div class="ai-header-badge">
        <span class="ai-badge"><span class="btn-sparkle">✨</span> AI Processing</span>
        <span class="stage-label" style="font-size:0.75rem; color:var(--ai-purple); font-weight:700;">Reasoning with LLaMA 3.3 70B...</span>
      </div>
      <div class="skeleton-line w-100"></div>
      <div class="skeleton-line w-80"></div>
    </div>
  `;

  try {
    const payload = {
      title: article.title,
      description: article.description,
      content: article.content,
      source: article.source,
      url: article.url,
    };

    const response = await fetch(`${API_BASE_URL}/api/simplify`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Failed to simplify article.");
    }

    const simplification = data.simplification;
    state.simplifiedMap.set(article.url, simplification);

    // Render structured results
    renderSummaryToCard(index, simplification);
    showToast("✨ Article simplified with LLaMA 3.3 70B", "success");
  } catch (error) {
    aiSlot.innerHTML = `
      <div class="ai-simplified-container" style="border-color: rgba(220, 38, 38, 0.4); background: var(--status-error-bg);">
        <div style="font-size:0.8125rem; font-weight:700; color:var(--status-error);">
          ⚠️ Simplification Failed
        </div>
        <div style="font-size:0.75rem; color:var(--muted-text);">
          ${escapeHtml(error.message)}
        </div>
      </div>
    `;
    showToast(`Error: ${error.message}`, "error");
  } finally {
    simplifyBtn.disabled = false;
    simplifyBtn.innerHTML = `<span class="btn-sparkle">✨</span> <span class="btn-label">Re-Simplify</span>`;
  }
}

function renderSummaryToCard(index, result) {
  const aiSlot = document.getElementById(`aiSlot_${index}`);
  if (!aiSlot || !result) return;

  const keyPointsHtml = (result.key_points || [])
    .map((point) => `<li class="key-point-item">${escapeHtml(point)}</li>`)
    .join("");

  const termsHtml = (result.financial_terms || [])
    .map(
      (termObj) => `
      <div class="term-chip" title="Click to view definition">
        <div class="term-name">
          <span>${escapeHtml(termObj.term)}</span>
          <span style="font-size:0.7rem; opacity:0.7;">ℹ️</span>
        </div>
        <div class="term-def">${escapeHtml(termObj.explanation)}</div>
      </div>
    `
    )
    .join("");

  const affectedGroupsHtml = (result.affected_groups || [])
    .map((grp) => `<span class="group-pill">${escapeHtml(grp)}</span>`)
    .join("");

  aiSlot.innerHTML = `
    <div class="ai-simplified-container" role="region" aria-label="AI Simplified Summary">
      <!-- Badge Header -->
      <div class="ai-header-badge">
        <span class="ai-badge">✨ AI Simplified</span>
        <span style="font-size:0.6875rem; color:var(--muted-text); font-weight:600;">Groq LLaMA 3.3 70B</span>
      </div>

      <!-- Plain English Summary -->
      <div class="ai-summary-text">
        ${escapeHtml(result.simple_summary)}
      </div>

      <!-- Key Takeaways -->
      ${
        result.key_points && result.key_points.length > 0
          ? `
        <div class="ai-section-block">
          <span class="ai-section-title">Key Takeaways</span>
          <ul class="key-points-list">${keyPointsHtml}</ul>
        </div>
      `
          : ""
      }

      <!-- Financial Terms Explained -->
      ${
        result.financial_terms && result.financial_terms.length > 0
          ? `
        <div class="ai-section-block">
          <span class="ai-section-title">Financial Jargon Decoded</span>
          <div class="terms-chips-container">${termsHtml}</div>
        </div>
      `
          : ""
      }

      <!-- Why It Matters -->
      ${
        result.why_it_matters
          ? `
        <div class="ai-section-block">
          <span class="ai-section-title">Why This Matters</span>
          <div class="callout-box">${escapeHtml(result.why_it_matters)}</div>
        </div>
      `
          : ""
      }

      <!-- Market Relevance -->
      ${
        result.market_relevance
          ? `
        <div class="ai-section-block">
          <span class="ai-section-title">Market Relevance</span>
          <div class="callout-box market-callout">${escapeHtml(result.market_relevance)}</div>
        </div>
      `
          : ""
      }

      <!-- Affected Groups -->
      ${
        result.affected_groups && result.affected_groups.length > 0
          ? `
        <div class="ai-section-block">
          <span class="ai-section-title">Potentially Affected Groups</span>
          <div class="affected-groups-pills">${affectedGroupsHtml}</div>
        </div>
      `
          : ""
      }
    </div>
  `;
}

// ==============================================================================
// 7. Batch Fetch & Simplify Workflow
// ==============================================================================

async function fetchAndSimplifyTopArticles() {
  if (state.isBatchSimplifying) return;
  state.isBatchSimplifying = true;

  const btn = elements.fetchAndSimplifyAllBtn;
  const originalText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = `<span class="spinner-ring" style="width:16px;height:16px;border-width:2px;"></span> Simplifying Feed...`;

  showToast("Fetching news and analyzing with LLaMA 3.3 70B...", "info");

  try {
    // 1. Fetch news if not loaded
    if (!state.articles || state.articles.length === 0) {
      await fetchNews({ category: state.currentCategory });
    }

    // 2. Select top 3-4 articles to simplify
    const topArticles = state.articles.slice(0, 4);
    if (topArticles.length === 0) {
      showToast("No articles available to simplify.", "error");
      return;
    }

    const batchPayload = {
      articles: topArticles.map((a) => ({
        title: a.title,
        description: a.description,
        content: a.content,
        source: a.source,
        url: a.url,
      })),
    };

    const response = await fetch(`${API_BASE_URL}/api/simplify/batch`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(batchPayload),
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.message || "Batch simplification failed.");
    }

    // Apply batch results
    (data.results || []).forEach((item, idx) => {
      if (item.simplification && item.article?.url) {
        state.simplifiedMap.set(item.article.url, item.simplification);
        renderSummaryToCard(idx, item.simplification);
      }
    });

    showToast(`Successfully simplified ${data.total_processed} articles with AI!`, "success");
  } catch (err) {
    showToast(`Batch error: ${err.message}`, "error");
  } finally {
    state.isBatchSimplifying = false;
    btn.disabled = false;
    btn.innerHTML = originalText;
  }
}

// ==============================================================================
// 8. Helper Utilities
// ==============================================================================

function formatRelativeTime(isoString) {
  if (!isoString) return "Recently";
  const date = new Date(isoString);
  if (isNaN(date.getTime())) return "Recently";

  const diffMs = Date.now() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffMinutes = Math.floor(diffMs / (1000 * 60));

  if (diffMinutes < 1) return "Just now";
  if (diffMinutes < 60) return `${diffMinutes}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function escapeHtml(text) {
  if (text === null || text === undefined) return "";
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}

function showToast(message, type = "info") {
  const toast = document.createElement("div");
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  elements.toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateY(10px)";
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// ==============================================================================
// 9. Demo / Sample Financial Articles
// ==============================================================================

const DEMO_ARTICLES = [
  {
    title: "Federal Reserve Holds Benchmark Interest Rates Steady Amid Cooling Inflation",
    description: "The Federal Reserve kept its benchmark lending rate unchanged on Wednesday, noting continued progress on lowering inflation while job growth remains resilient.",
    content: "WASHINGTON — Federal Reserve policymakers voted unanimously to maintain the federal funds rate between 5.25% and 5.50%. Chair Jerome Powell indicated that while economic expansion remains solid, the central bank wants greater confidence that inflation is moving sustainably toward its 2% target before lowering borrowing costs.",
    source: "Reuters",
    author: "Howard Schneider",
    published_at: new Date(Date.now() - 1000 * 60 * 75).toISOString(),
    url: "https://www.reuters.com/markets/us/fed-holds-rates-steady-2026",
    image_url: "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80"
  },
  {
    title: "Semiconductor Giants Lead Market Rally on Surging Artificial Intelligence Demand",
    description: "Major technology indices gained as leading chipmakers reported record quarterly revenue and expanded enterprise cloud infrastructure guidance.",
    content: "SAN FRANCISCO — The Nasdaq Composite advanced 1.8% today, propelled by unprecedented demand for high-performance graphics processing units and data center accelerators. Analysts noted strong corporate capital expenditure trends across global enterprise software firms.",
    source: "Bloomberg",
    author: "Ian King",
    published_at: new Date(Date.now() - 1000 * 60 * 180).toISOString(),
    url: "https://www.bloomberg.com/news/articles/tech-rally-ai-semiconductors",
    image_url: "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80"
  },
  {
    title: "U.S. Consumer Price Index Rises 0.2% in Latest Monthly Reading",
    description: "Annual inflation slowed to 2.4%, marking its lowest level in over three years, led by declines in gasoline and energy prices.",
    content: "WASHINGTON — The Consumer Price Index (CPI) increased 0.2% on a seasonally adjusted basis last month, according to the Bureau of Labor Statistics. Core CPI, which excludes volatile food and energy components, rose 0.3%, meeting consensus economist expectations.",
    source: "Wall Street Journal",
    author: "Gwynn Guilford",
    published_at: new Date(Date.now() - 1000 * 60 * 320).toISOString(),
    url: "https://www.wsj.com/economy/central-banking/us-cpi-inflation-report-2026",
    image_url: "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80"
  },
  {
    title: "Global Crude Oil Prices Dip Following Unexpected Build in Commercial Inventories",
    description: "Brent crude futures declined 1.4% toward $74 per barrel as commercial stockpiles increased and manufacturing data signaled moderate demand.",
    content: "HOUSTON — West Texas Intermediate and Brent crude futures slipped today following the Energy Information Administration's report of a 3.2 million barrel increase in domestic commercial reserves, easing immediate supply shortage concerns across global energy markets.",
    source: "Financial Times",
    author: "Derek Brower",
    published_at: new Date(Date.now() - 1000 * 60 * 480).toISOString(),
    url: "https://www.ft.com/content/oil-prices-eia-inventories-2026",
    image_url: "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?auto=format&fit=crop&w=800&q=80"
  }
];

const DEMO_SIMPLIFICATIONS = {
  "https://www.reuters.com/markets/us/fed-holds-rates-steady-2026": {
    simple_summary: "The Federal Reserve decided to keep interest rates right where they are instead of raising or lowering them, because price increases in the economy are gradually cooling down.",
    key_points: [
      "Benchmark lending rates remain steady between 5.25% and 5.50%.",
      "Inflation is moving closer toward the central bank's 2.0% annual target.",
      "Policymakers are waiting for more economic reports before considering future rate reductions."
    ],
    financial_terms: [
      {
        term: "Benchmark Interest Rate",
        explanation: "The standard lending rate set by a central bank that directly influences what regular commercial banks charge consumers for mortgages, auto loans, and credit cards."
      },
      {
        term: "Federal Funds Rate",
        explanation: "The overnight interest rate at which commercial banks borrow and lend reserve funds to each other."
      }
    ],
    why_it_matters: "This means monthly payments on credit cards, car loans, and new mortgages will stay relatively stable for now, rather than getting more expensive.",
    market_relevance: "The article reports that financial markets welcomed the decision with stability, as the outcome matched economist forecasts without unexpected policy changes.",
    affected_groups: [
      "Homebuyers & Mortgage Borrowers",
      "Credit Card Users",
      "Commercial Banks"
    ]
  },
  "https://www.bloomberg.com/news/articles/tech-rally-ai-semiconductors": {
    simple_summary: "Technology stocks surged higher today after major semiconductor companies announced strong sales figures and increased business demand for artificial intelligence hardware.",
    key_points: [
      "The tech-heavy Nasdaq index rose 1.8% during trading.",
      "Chipmakers reported record revenue from artificial intelligence data centers.",
      "Major global corporations continue spending heavily on computer infrastructure."
    ],
    financial_terms: [
      {
        term: "Nasdaq Composite",
        explanation: "A major stock market index consisting primarily of technology and innovation-focused publicly traded companies."
      },
      {
        term: "Capital Expenditure (CapEx)",
        explanation: "The money a business spends on physical equipment, computers, and infrastructure to grow its operations."
      }
    ],
    why_it_matters: "The growing demand indicates that enterprise technology spending remains robust, which can support jobs and economic growth in the tech sector.",
    market_relevance: "According to the article, semiconductor and hardware shares led broad gains across global stock markets.",
    affected_groups: [
      "Tech Sector Investors",
      "Enterprise Software Companies",
      "Data Center Providers"
    ]
  }
};

function loadDemoArticles() {
  hideLoading();
  hideError();
  hideEmpty();
  
  state.articles = [...DEMO_ARTICLES];
  // Pre-seed demo simplifications
  Object.entries(DEMO_SIMPLIFICATIONS).forEach(([url, simp]) => {
    state.simplifiedMap.set(url, simp);
  });

  elements.resultsCountText.textContent = `Showing ${state.articles.length} curated demo financial articles`;
  renderNews(state.articles);
  showToast("✨ Loaded demo financial news with instant AI summaries!", "success");
}

