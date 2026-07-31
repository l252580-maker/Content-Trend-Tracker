from datetime import date, timedelta

COVERED_TOPIC_TTL_DAYS = 30  # how long a covered topic stays in already_covered.csv

def readAlreadyCoveredTopics():
    with open("data/already_covered.csv", "r") as covered:
        covered_cntnt = covered.read()
        covered_lines = covered_cntnt.splitlines()  # This line splits the content into lines and stores it in a variable
        if (len(covered_lines) == 0):
            print("No topics have been covered yet")
            return []

    header = covered_lines[0]
    rows = covered_lines[1:]

    # Drop topics that were added more than 30 days ago
    cutoff = date.today() - timedelta(days=COVERED_TOPIC_TTL_DAYS)
    kept_rows = []
    for row in rows:
        topic, added_on = row.split(",")
        if date.fromisoformat(added_on) >= cutoff:
            kept_rows.append(row)

    # If any topics expired, rewrite the file without them
    if len(kept_rows) != len(rows):
        with open("data/already_covered.csv", "w") as covered:
            covered.write(header + "\n")
            for row in kept_rows:
                covered.write(row + "\n")

    return [header] + kept_rows

def searchHistory(query):
    """
    Search already-covered topics by keyword.

    Args:
        query (str): Search term.

    Returns:
        list[str]: Matching "Topic,Date" lines from already_covered.csv.
    """
    
    covered = readAlreadyCoveredTopics()
    for row in covered:
        if query.lower() in row.lower():
            print("\n")
            print(row)
        else:
            print("No matching topics found for the query: " + query)