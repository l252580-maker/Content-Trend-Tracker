from src.api import fetchNewsForTopic

news = fetchNewsForTopic("Pakistan")
print(news[0]['author'])