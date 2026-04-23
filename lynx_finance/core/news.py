"""News fetching for Financials companies."""

from __future__ import annotations

from typing import Optional

import feedparser
import requests
import yfinance as yf

from lynx_finance import NEWS_SECTOR_KEYWORD, USER_AGENT_PRODUCT
from lynx_finance.core.storage import get_news_dir, save_json, save_text
from lynx_finance.models import NewsArticle


def fetch_news_yfinance(ticker: str) -> list[NewsArticle]:
    try:
        t = yf.Ticker(ticker)
    except Exception:
        return []
    articles: list[NewsArticle] = []
    try:
        news_items = t.news or []
    except Exception:
        news_items = []
    for item in news_items:
        content = item.get("content", item) if isinstance(item, dict) else item
        if isinstance(content, dict):
            title = content.get("title", "")
            url = content.get("canonicalUrl", {})
            if isinstance(url, dict):
                url = url.get("url", "")
            elif not isinstance(url, str):
                url = content.get("link", "")
            pub = content.get("pubDate") or content.get("providerPublishTime", "")
            source = content.get("provider", {})
            if isinstance(source, dict):
                source = source.get("displayName", "")
            summary = content.get("summary", "")
        else:
            continue
        articles.append(NewsArticle(title=title, url=url if isinstance(url, str) else "",
                                    published=str(pub), source=source if isinstance(source, str) else "",
                                    summary=summary))
    return articles


def fetch_news_rss(company_name: str, ticker: str) -> list[NewsArticle]:
    query = f"{company_name} {ticker} {NEWS_SECTOR_KEYWORD}"
    feed_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en&gl=US&ceid=US:en"
    articles: list[NewsArticle] = []
    try:
        feed = feedparser.parse(feed_url)
        for entry in feed.entries[:20]:
            articles.append(NewsArticle(
                title=entry.get("title", ""), url=entry.get("link", ""),
                published=entry.get("published", ""),
                source=entry.get("source", {}).get("title", "") if isinstance(entry.get("source"), dict) else "",
                summary=entry.get("summary", ""),
            ))
    except Exception:
        pass
    return articles


def fetch_all_news(ticker: str, company_name: Optional[str] = None) -> list[NewsArticle]:
    articles: list[NewsArticle] = []
    articles.extend(fetch_news_yfinance(ticker))
    name = company_name or ticker
    rss_news = fetch_news_rss(name, ticker)
    existing_titles = {a.title.lower().strip() for a in articles}
    for art in rss_news:
        if art.title.lower().strip() not in existing_titles:
            articles.append(art)
            existing_titles.add(art.title.lower().strip())
    ndir = get_news_dir(ticker)
    save_json(ndir / "news_index.json", [
        {"title": a.title, "url": a.url, "published": a.published, "source": a.source, "summary": a.summary}
        for a in articles
    ])
    return articles


def download_article(ticker: str, article: NewsArticle) -> Optional[str]:
    from lynx_investor_core.urlsafe import is_safe_url
    if not is_safe_url(article.url):
        return None
    if not article.url:
        return None
    ndir = get_news_dir(ticker)
    safe_title = "".join(c if c.isalnum() or c in " -_" else "" for c in article.title)[:60].strip()
    path = ndir / f"{safe_title}.txt"
    try:
        resp = requests.get(article.url, timeout=15, allow_redirects=False, headers={"User-Agent": f"Mozilla/5.0 (compatible; {USER_AGENT_PRODUCT})"})
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        for tag in soup(["script", "style", "nav", "header", "footer"]):
            tag.decompose()
        text = soup.get_text(separator="\n", strip=True)[:50000]
        save_text(path, f"Title: {article.title}\nURL: {article.url}\nPublished: {article.published}\nSource: {article.source}\n\n{text}")
        article.local_path = str(path)
        return str(path)
    except Exception:
        return None
