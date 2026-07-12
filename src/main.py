from history import readAlreadyCoveredTopics

def addNewTopic(topic):
    with open("data/already_covered.csv", "a") as covered:
        covered.write(topic + "\n")

with open("data/topics.csv", "r") as topics:
    content = topics.read()
print(content)

print("\nAlready covered topics:\n")
readAlreadyCoveredTopics()