def readAlreadyCoveredTopics():
    with open("data/already_covered.csv", "r") as covered:
        covered_cntnt = covered.read()
        covered_lines = covered_cntnt.splitlines()  # This line splits the content into lines and stores it in a variable
        covered_lines = covered_lines[1:]
        if (len(covered_lines) == 0):
            print("No topics have been covered yet")
            return []

    return covered_lines
