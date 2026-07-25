def readAlreadyCoveredTopics():
    with open("data/already_covered.csv", "r") as covered:
        covered_cntnt = covered.read()
    return covered_cntnt.splitlines()
