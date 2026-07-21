from src.history import readAlreadyCoveredTopics
from src.api import fetchNewsForAllTopics
from src.api import extractArticleInfo
from src.api import storeNews

def addNewTopic(topic):
    with open("data/already_covered.csv", "a") as covered:
        covered.write(topic + "\n")

def callExtractArticleInfo(news):
    for topic, articles in news.items():
        print(f"\n{topic}")

        clean_arts = []
        for article in articles:
            article_info = extractArticleInfo(article)
            clean_arts.append(article_info)
        storeNews(topic, clean_arts)

# ---------------------------------------MAIN----------------------------------------

news = {}
with open("data/topics.csv", "r") as topics:
    content = topics.read().splitlines()
    content = content[1:]  # Skip the header row
    news = fetchNewsForAllTopics(content)
print(content)

callExtractArticleInfo(news)

print("\nAlready covered topics:\n")
readAlreadyCoveredTopics()