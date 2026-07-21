from src.history import readAlreadyCoveredTopics
from src.api import fetchNewsForAllTopics
from src.api import extractArticleInfo

def addNewTopic(topic):
    with open("data/already_covered.csv", "a") as covered:
        covered.write(topic + "\n")

def callExtractArticleInfo(news):
    for topic, articles in news.items():
        print(f"\n{topic}")

        for article in articles:
            article_info = extractArticleInfo(article)
            article_info.display()

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