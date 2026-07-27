def readAlreadyCoveredTopics():
    with open("data/already_covered.csv", "r") as covered:
        covered_cntnt = covered.read()
        covered_lines = covered_cntnt.splitlines()  # This line splits the content into lines and stores it in a variable
        if (len(covered_lines) == 0):
            print("No topics have been covered yet")
            return []

    return covered_lines

def searchHistory(query):
    """
    Search already-covered topics by keyword.

    Args:
        query (str): Search term.

    Returns:
        list[str]: Matching "Topic,Date" lines from already_covered.csv.
    """
    # TODO: Call readAlreadyCoveredTopics() and filter lines by query (case-insensitive)
    covered = readAlreadyCoveredTopics()
    for row in covered:
        if query.lower() in row.lower():
            print("\n")
            print(row)
        else:
            print("No matching topics found for the query: " + query)