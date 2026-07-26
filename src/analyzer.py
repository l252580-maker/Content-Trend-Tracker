# from .models import Topic, Recommendation
import os
import csv
from .history import readAlreadyCoveredTopics
from dateutil import parser as date_parser
from datetime import datetime, timezone
from .models import Topic, Recommendation

"""
Phase 3: Data Processing & Recommendation Engine

Analyzes collected news data (from data/news/<topic>.csv), scores topics
by relevance, ranks them, cross-checks against already_covered.csv, and
produces a shortlist of recommended content ideas.
"""

def loadNewsForTopic(topic):
    """
    Load previously stored articles for a topic from data/news/<topic>.csv.

    Args:
        topic (str): Topic name.

    Returns:
        list[dict]: Raw rows read from the topic's CSV file.
    """
    # Open data/news/<topic>.csv with csv.DictReader
    filepath = f"data/news/{topic}.csv"
    exist = os.path.exists(filepath)
    if not exist:
        print("No file")
        return []

    records = []
    with open(filepath, "r", newline="") as topic_detail:
        reader = csv.DictReader(topic_detail)
        for row in reader:
            records.append(row)

    return records

def cleanArticles(articles):
    """
    Clean and preprocess raw article rows before scoring.

    Args:
        articles (list[dict]): Raw article rows for a topic.

    Returns:
        list[dict]: Cleaned/normalized article rows.
    """
    # Handle missing/empty fields (e.g. blank description or published_at)
    if len(articles) == 0:
        return []
    
    cleaned_arts = []
    urls = set()  # Track seen URLs to drop duplicates
    for article in articles:
        url = article.get("url")
        if not url:
            continue

        if url in urls:
            continue  # Skip duplicate article by URL
        urls.add(url)
        cleaned_arts.append(article)

    # Normalize published_at into a comparable datetime
    for article in cleaned_arts:
        date = article.get("published_at")
        if date:
            try:
                print(type(date), repr(date))
                parsed_date = date_parser.parse(date)
                article["published_at"] = parsed_date
            except ValueError:
                continue  # Skip articles with invalid dates
        else:
            continue  # Skip articles without a valid date

        descr = article.get("description")
        if descr == None:
            article["description"] = ""  # Replace None with empty string
    
    return cleaned_arts

def calculateRelevanceScore(articles):
    """
    Calculate a relevance score for a topic based on article count and recency.

    Args:
        articles (list[dict]): Cleaned articles for the topic.

    Returns:
        float: Relevance score for the topic.
    """
    # Factor in number of articles
    if len(articles) == 0:
        return 0.0
    
    this_instant = datetime.now(timezone.utc)
    art_count = len(articles)
    score = None

    recency_score = 0.0
    for article in articles:
        date = article.get("published_at")
        if not date:
            continue

        time_passed = (this_instant - date).total_seconds() / 3600 # Time passed in hours
        recency = 1 / (1 + time_passed)  # More recent articles contribute more

        recency_score = max(recency_score, recency)

    score = recency_score + art_count
    
    return score


def rankTopics(topic_scores):
    """
    Rank topics according to their relevance scores.

    Args:
        topic_scores (dict[str, float]): Mapping of topic -> relevance score.

    Returns:
        list[Topic]: Topics sorted from most to least relevant.
    """
    # Build Topic objects (or update existing ones) with relevance_score set
    topics = []
    for topic_name, score in topic_scores.items():
        topic = Topic(topic_name)
        topic.setRelevanceScore(score)
        topics.append(topic)

    for i in range(len(topics)):
        for j in range(i + 1, len(topics)):
            if topics[j].relevance_score > topics[i].relevance_score:
                temp = topics[i]
                topics[i] = topics[j]
                topics[j] = temp

    return topics


def loadAlreadyCoveredTopics():
    """
    Load the list of already-covered topics from data/already_covered.csv.

    Returns:
        list[str]: Topic names that have already been covered.
    """
    return readAlreadyCoveredTopics()


def filterOutCoveredTopics(ranked_topics, covered_topics):
    """
    Compare ranked topics against already-covered topics to flag repeats.

    Args:
        ranked_topics (list[Topic]): Topics sorted by relevance.
        covered_topics (list[str]): Topics already covered.

    Returns:
        list[Topic]: Ranked topics with covered ones filtered out or flagged.
    """
    # Cross-reference ranked_topics against covered_topics
    if len(ranked_topics) == 0 or len(covered_topics) == 0:
        return ranked_topics

    filtered_topics = []
    for ranked in ranked_topics:
        is_covered = False

        for topic in covered_topics:
            if topic.lower().split(',')[0] in ranked.name.lower():
                is_covered = True
                break

        if not is_covered:
            filtered_topics.append(ranked)

    return filtered_topics


def generateRecommendations(ranked_topics, limit=5):
    """
    Generate a prioritized shortlist of recommended content ideas.

    Args:
        ranked_topics (list[Topic]): Topics sorted by relevance (covered ones filtered/flagged).
        limit (int): Max number of recommendations to return.

    Returns:
        list[Recommendation]: Top recommended topics for new content.
    """
    # Wrap top N topics into Recommendation objects
    recommendations = []
    for i in range(min(limit, len(ranked_topics))):
        topic = ranked_topics[i]
        score = topic.relevance_score
        recommendation = Recommendation(topic, score)
        # Add recommendation to a list (not shown in this snippet)
        recommendations.append(recommendation)

    # Return the shortlist
    return recommendations