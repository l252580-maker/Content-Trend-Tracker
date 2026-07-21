from src.api import extractArticleInfo
from src.api import fetchNewsForAllTopics
from src.models import NewsArticle

list = ["Pakistan", "India", "USA"]
news = fetchNewsForAllTopics(list)

for topic, articles in news.items():
    print(f"\n{topic}")

    for article in articles:
        article_info = extractArticleInfo(article)
        article_info.display()