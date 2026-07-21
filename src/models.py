class Topic:
    """
    Represents a predefined topic being tracked by the application.
    """

    def __init__(self, name):
        # TODO: Store the topic name
        # TODO: (Phase 3) add a relevance_score attribute, default None or 0
        pass


class NewsArticle:
    """
    Represents a single news article retrieved from the News API,
    with only the fields the app actually needs.
    """

    def __init__(self, title, source, published_at, description, url):
        # TODO: Assign title, source, published_at, description, url to instance attributes
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
        # TODO: Assign topic and score to instance attributes
        pass