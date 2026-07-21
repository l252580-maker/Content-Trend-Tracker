from src.api import fetchNewsForAllTopics

topics = ["Pakistan", "India", "USA"]
news_dict = fetchNewsForAllTopics(topics)
print(news_dict["Pakistan"][0]['author'])
print(news_dict["India"][0]['author'])
print(news_dict["USA"][0]['author'])
print(news_dict["Pakistan"][0]['title'])
print(news_dict["India"][0]['title'])
print(news_dict["USA"][0]['title'])
print(news_dict["Pakistan"][0]['description'])
print(news_dict["India"][0]['description'])
print(news_dict["USA"][0]['description'])