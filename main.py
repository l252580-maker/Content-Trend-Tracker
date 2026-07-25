from src.api import fetchNewsForAllTopics
from src.api import extractArticleInfo
from src.api import storeNews
from pathlib import Path
from src.analyzer import loadNewsForTopic
from src.analyzer import cleanArticles
from src.analyzer import calculateRelevanceScore
from src.analyzer import rankTopics
from src.analyzer import loadAlreadyCoveredTopics
from src.analyzer import filterOutCoveredTopics
from src.analyzer import generateRecommendations

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

def analyzeNews():
    news = Path("data/news")

    topics_scores = {}
    for topic_csv in news.iterdir():
        topic = topic_csv.stem
        articles = loadNewsForTopic(topic)
        print(f"Loaded: {len(articles)} articles")

        cleaned_arts = cleanArticles(articles)
        print(f"Cleaned: {len(cleaned_arts)} articles")

        print(f"Calculating relevance score for {topic}...")
        score = calculateRelevanceScore(cleaned_arts)
        topics_scores[topic] = score

        sorted_topics = rankTopics(topics_scores)

    return sorted_topics


# ---------------------------------------MAIN----------------------------------------

news = {}
with open("data/topics.csv", "r") as topics:
    content = topics.read().splitlines()
    content = content[1:]  # Skip the header row
    news = fetchNewsForAllTopics(content)

callExtractArticleInfo(news)

sorted_topics = analyzeNews()
covered = loadAlreadyCoveredTopics()
filtered = filterOutCoveredTopics(sorted_topics, covered)
recommendations = generateRecommendations(filtered) # is a list of Recommendation objects

for recommendation in recommendations:
    topic = recommendation.topic
    score = recommendation.score
    print(f"Recommended Topic: {topic.name}, Score: {score:.2f}")