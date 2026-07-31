class Topic:
    """
    Represents a predefined topic being tracked by the application.
    """

    def __init__(self, name):
        self.name = name
        self.relevance_score = None

    def setRelevanceScore(self, score):
        self.relevance_score = score

class NewsArticle:
    """
    Represents a single news article retrieved from the News API,
    with only the fields the app actually needs.
    """

    def __init__(self, title, source, published_at, description, url):
        
        self.title = title
        self.source = source
        self.published_at = published_at
        self.description = description
        self.url = url

    def display(self):
        print(f"Title: {self.title}")
        print(f"Source: {self.source}")
        print(f"Published At: {self.published_at}")
        print(f"Description: {self.description}")
        print(f"URL: {self.url}")


class Recommendation:
    """
    Represents a ranked topic recommendation produced by the
    analysis/recommendation engine (Phase 3).
    """

    def __init__(self, topic, score):
        self.topic = topic
        self.score = score