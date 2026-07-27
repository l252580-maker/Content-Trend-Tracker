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
from tabulate import tabulate
from src.history import searchHistory

def addNewTopic(topic):
    from datetime import date
    with open("data/already_covered.csv", "a") as covered:
        covered.write(f"{topic},{date.today()}\n")

def callExtractArticleInfo(news):
    for topic, articles in news.items():
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

"""
Phase 4: User Interface & Content History

Provides a command-line interface for displaying recommendations,
marking topics as covered, and viewing/searching coverage history.
"""

def displayRecommendations(recommendations):
    """
    Display ranked topic recommendations in a readable CLI format.

    Args:
        recommendations (list[Recommendation]): Ranked recommendations from generateRecommendations().
    """
    rows = []

    for recommendation in recommendations:
        rows.append([
            recommendation.topic.name,
            recommendation.score
        ])

    print(tabulate(
        rows,
        headers=["Topic", "Relevance Score"],
        tablefmt="fancy_grid"
    ))


def promptMarkAsCovered(recommendations):
    choosed_topic = input("Enter the topic from recommendations that you have choosed: ")
    for recommendation in recommendations:
        if recommendation.topic.name == choosed_topic:
            return recommendation.topic
    print(f"No match found for: {choosed_topic!r}")  # TEMP debug
    return None



def confirmMarkAsCovered(topic):
    """
    Ask the user to confirm before writing a topic to already_covered.csv.

    Args:
        topic (Topic): The topic pending confirmation.

    Returns:
        bool: True if confirmed, False otherwise.
    """
    # TODO: Prompt y/n confirmation
    conformation = input(f"Are you sure you want to mark '{topic.name}' as covered? (y/n): ")
    if conformation.lower() == 'y':
        return True
    else:   
        return False


def displayCoveredTopics(covered_topics):
    """
    Display previously covered topics (topic + date) in a readable format.

    Args:
        covered_topics (list[str]): Raw "Topic,Date" lines from readAlreadyCoveredTopics().
    """
    # TODO: Parse each line into topic/date and print in a readable table
    rows = []
    for line in covered_topics:
        topic, date = line.split(",")
        rows.append([topic, date])

    print(tabulate(
        rows,
        headers="firstrow",
        tablefmt="fancy_grid"
    ))


# ---------------------------------------MAIN----------------------------------------

print("Welcome to the Content Trend Tracker!")
print("Running! This won't take much tieme, please wait...")
print("\n")
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

choice = None
while choice != 0:
    print("\n")
    print("Welcome to the Content Trend Tracker!")
    print("Running! This won't take much time, please wait...")
    print("\n")
    print("-----Menu-----")
    print("\n")
    print("Press:")
    print("1. View Recommendations")
    print("2. Display Covered Topics")
    print("3. Search Covered Topics")
    print("4. Choose a recommended topic: ")
    print("0. Exit")

    choice = int(input("Enter your choice: "))
    if choice == 1:
        displayRecommendations(recommendations)
    elif choice == 2:
        displayCoveredTopics(covered)
    elif choice == 3:
        query = input("Enter search term: ")
        searchHistory(query)

    elif choice == 4:
        chosen_topic = promptMarkAsCovered(recommendations)
        if chosen_topic:
            if confirmMarkAsCovered(chosen_topic):
                addNewTopic(chosen_topic.name)
                print(f"Topic '{chosen_topic.name}' marked as covered.")
            else:
                print("Operation cancelled.")
