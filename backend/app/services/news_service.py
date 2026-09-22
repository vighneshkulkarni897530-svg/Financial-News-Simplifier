"""NewsAPI integration service with deduplication, validation, and in-memory TTL caching."""

import time
from typing import Dict, List, Optional, Tuple
import httpx

from app.core.config import settings
from app.core.logging_config import logger
from app.schemas.news_schema import Article, NewsResponse
from app.utils.text_cleaner import normalize_title_for_dedup


class NewsServiceException(Exception):
    """Custom exception for NewsAPI operations."""

    def __init__(self, code: str, message: str, status_code: int = 500, details: Optional[dict] = None):
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code
        self.details = details or {}


CATEGORY_QUERIES = {
    "all": "stock market OR economy OR inflation OR finance OR central bank OR earnings",
    "markets": "stock market OR Wall Street OR Nasdaq OR S&P 500 OR bond yields OR trading",
    "economy": "Federal Reserve OR inflation OR GDP OR interest rates OR unemployment OR treasury",
    "business": "corporate earnings OR revenue OR merger acquisition OR startup OR CEO",
    "technology": "tech stocks OR artificial intelligence OR semiconductors OR cloud computing",
}


class NewsService:
    """Async service to fetch, sanitize, deduplicate, and cache financial news."""

    def __init__(self):
        self.base_url = "https://newsapi.org/v2"
        # Cache structure: key -> (timestamp, list of articles)
        self._cache: Dict[str, Tuple[float, List[Article]]] = {}

    def _get_cache_key(self, query: Optional[str], category: Optional[str], page: int, page_size: int) -> str:
        return f"q={query or ''}::cat={category or 'all'}::p={page}::ps={page_size}"

    def _get_cached_articles(self, cache_key: str) -> Optional[List[Article]]:
        if cache_key in self._cache:
            cached_time, articles = self._cache[cache_key]
            ttl_seconds = settings.NEWS_CACHE_MINUTES * 60
            if (time.time() - cached_time) < ttl_seconds:
                logger.info(f"Cache hit for key: {cache_key} ({len(articles)} articles)")
                return articles
            else:
                del self._cache[cache_key]
        return None

    def _set_cached_articles(self, cache_key: str, articles: List[Article]) -> None:
        self._cache[cache_key] = (time.time(), articles)

    def _normalize_and_filter_articles(self, raw_articles: List[dict]) -> List[Article]:
        """Validate, deduplicate, and normalize raw NewsAPI articles."""
        normalized: List[Article] = []
        seen_urls = set()
        seen_titles = set()

        for item in raw_articles:
            if not isinstance(item, dict):
                continue

            title = (item.get("title") or "").strip()
            url = (item.get("url") or "").strip()

            # Skip removed or empty articles
            if not title or title.lower() == "[removed]" or not url or url.lower() == "https://removed.com":
                continue

            # Skip duplicates by URL
            if url in seen_urls:
                continue

            # Extract source name
            source_raw = item.get("source")
            source_name = "Financial News"
            if isinstance(source_raw, dict):
                source_name = (source_raw.get("name") or "").strip() or "Financial News"
            elif isinstance(source_raw, str) and source_raw.strip():
                source_name = source_raw.strip()

            # Deduplicate by normalized title + source
            title_key = normalize_title_for_dedup(title, source_name)
            if title_key in seen_titles:
                continue

            seen_urls.add(url)
            seen_titles.add(title_key)

            description = item.get("description")
            content = item.get("content")
            author = item.get("author")
            published_at = item.get("publishedAt")
            image_url = item.get("urlToImage")

            # Validate basic image url formatting
            if image_url and not (str(image_url).startswith("http://") or str(image_url).startswith("https://")):
                image_url = None

            article = Article(
                title=title,
                description=description if isinstance(description, str) and description.strip() else None,
                content=content if isinstance(content, str) and content.strip() else None,
                source=source_name,
                author=author if isinstance(author, str) and author.strip() else None,
                published_at=published_at if isinstance(published_at, str) else None,
                url=url,
                image_url=image_url if isinstance(image_url, str) else None,
            )
            normalized.append(article)

        return normalized

    async def get_financial_news(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 10,
    ) -> NewsResponse:
        """Fetch financial news from NewsAPI with caching and deduplication."""
        # Check API key configuration
        if not settings.is_news_api_configured:
            logger.error("NEWS_API_KEY is not configured in settings")
            raise NewsServiceException(
                code="MISSING_CONFIGURATION",
                message="NewsAPI key is not configured. Please set NEWS_API_KEY in your .env file.",
                status_code=503,
            )

        page = max(1, page)
        page_size = min(max(1, page_size), 50)
        selected_category = (category or "all").lower()

        # Check in-memory cache
        cache_key = self._get_cache_key(query, selected_category, page, page_size)
        cached_result = self._get_cached_articles(cache_key)
        if cached_result is not None:
            return NewsResponse(
                status="success",
                total_results=len(cached_result),
                articles=cached_result,
                query=query,
                category=selected_category,
            )

        # Build query parameters
        if query and query.strip():
            search_term = query.strip()
            # If user query doesn't specify financial terms, keep search focused
            q_param = f"({search_term}) AND (finance OR market OR economy OR stock OR business)"
        else:
            q_param = CATEGORY_QUERIES.get(selected_category, CATEGORY_QUERIES["all"])

        params = {
            "q": q_param,
            "language": "en",
            "sortBy": "publishedAt",
            "page": page,
            "pageSize": page_size,
            "apiKey": settings.NEWS_API_KEY,
        }

        url = f"{self.base_url}/everything"

        try:
            logger.info(f"Fetching news from NewsAPI: query='{query}', category='{selected_category}', page={page}")
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)

            if response.status_code == 401 or response.status_code == 403:
                logger.error(f"NewsAPI authentication error: {response.status_code}")
                raise NewsServiceException(
                    code="NEWS_API_ERROR",
                    message="Invalid or unauthorized NewsAPI key. Please check your NEWS_API_KEY.",
                    status_code=401,
                )
            elif response.status_code == 429:
                logger.warning("NewsAPI rate limit exceeded")
                raise NewsServiceException(
                    code="NEWS_API_RATE_LIMIT",
                    message="NewsAPI rate limit reached. Please try again later.",
                    status_code=429,
                )
            elif response.status_code != 200:
                logger.error(f"NewsAPI error {response.status_code}: {response.text}")
                raise NewsServiceException(
                    code="NEWS_API_ERROR",
                    message=f"NewsAPI returned status code {response.status_code}.",
                    status_code=502,
                )

            data = response.json()
            if data.get("status") != "ok":
                err_msg = data.get("message", "Unknown NewsAPI error")
                logger.error(f"NewsAPI reported status error: {err_msg}")
                raise NewsServiceException(
                    code="NEWS_API_ERROR",
                    message=f"NewsAPI error: {err_msg}",
                    status_code=502,
                )

            raw_articles = data.get("articles", [])
            normalized_articles = self._normalize_and_filter_articles(raw_articles)

            if not normalized_articles and page == 1:
                logger.info("No matching financial articles found for query")

            # Cache the normalized articles
            self._set_cached_articles(cache_key, normalized_articles)

            return NewsResponse(
                status="success",
                total_results=len(normalized_articles),
                articles=normalized_articles,
                query=query,
                category=selected_category,
            )

        except httpx.TimeoutException:
            logger.error("NewsAPI request timed out")
            raise NewsServiceException(
                code="NEWS_API_TIMEOUT",
                message="NewsAPI request timed out while fetching articles. Please try again.",
                status_code=504,
            )
        except httpx.RequestError as exc:
            logger.error(f"NewsAPI network connection error: {exc}")
            raise NewsServiceException(
                code="NEWS_API_ERROR",
                message=f"Failed to connect to NewsAPI: {str(exc)}",
                status_code=502,
            )


# Global singleton instance
news_service = NewsService()
