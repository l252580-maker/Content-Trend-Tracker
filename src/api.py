import os
import requests
from dotenv import load_dotenv
import time
from .models import NewsArticle
import csv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"


def fetchNewsForTopic(topic):
    """
    Fetch recent news articles for a single topic from the News API.

    Args:
        topic (str): The topic/keyword to search for.

    Returns:
        list[dict]: Raw article objects returned by the API.
    """
    # Build request params (q=topic, apiKey=NEWS_API_KEY, sortBy="publishedAt", language="en")
    params = {
        "q" : topic,
        "apiKey" : NEWS_API_KEY,
        "sortBy" : "publishedAt",
        "language" : "en"
    }

    # Send GET request to BASE_URL using requests.get(params=...)
    response = requests.get(BASE_URL, params=params, timeout = 10)

    # Handle non-200 responses and network errors (raise or log, don't crash silently)
    if response.status_code != 200:
        print("Error fetching news")
        return []

    # Return response.json()["articles"]
    data = response.json()
    return data.get("articles", [])


def fetchNewsForAllTopics(topics):
    """
    Fetch recent news for a list of topics.

    Args:
        topics (list[str]): List of topic names (e.g. loaded from topics.csv).

    Returns:
        dict[str, list[dict]]: Mapping of topic -> list of raw articles.
    """
    # Loop through topics and call fetchNewsForTopic(topic) for each
    result = {}
    for topic in topics:
        news = fetchNewsForTopic(topic)
        result[topic] = news
        time.sleep(5)  # Delay between requests to avoid hitting API rate limits

    return result


def extractArticleInfo(article):
    """
    Extract the relevant fields from a raw article dict returned by the API.

    Args:
        article (dict): A single raw article object from the News API response.

    Returns:
        NewsArticle: A cleaned, structured representation of the article.
    """
    # Pull out title, source.name, publishedAt, description, url
    title = article.get("title")
    name = article.get("source", {}).get("name")
    published_at = article.get("publishedAt")
    description = article.get("description")
    url = article.get("url")
    # Wrap the extracted fields in a models.NewsArticle instance
    news_article = NewsArticle(title, name, published_at, description, url)
    return news_article


def storeNews(topic, articles):
    """
    Persist retrieved news articles locally so they can be analyzed later
    (by analyzer.py in Phase 3).

    Args:
        topic (str): The topic the articles belong to.
        articles (list[NewsArticle]): Cleaned article data to store.
    """
    # TODO: Decide on a storage location/format under data/ (e.g. data/news/<topic>.csv)
    # TODO: Write articles to disk, avoiding duplicate entries on repeated runs
    pass
