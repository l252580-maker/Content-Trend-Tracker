import time  # add if not already imported

ONE_MONTH_SECONDS = 30 * 24 * 60 * 60  # matches "1 month" retention window


def deleteExpiredNewsFiles(news_dir="data/news"):
    """
    Delete topic CSV files under data/news/ that are older than 1 month
    from their creation date.
    """
    if not os.path.exists(news_dir):
        return

    now = time.time()

    for filename in os.listdir(news_dir):
        if not filename.endswith(".csv"):
            continue

        filepath = os.path.join(news_dir, filename)
        created_at = os.path.getctime(filepath)
        age_seconds = now - created_at

        if age_seconds > ONE_MONTH_SECONDS:
            os.remove(filepath)
            print(f"Deleted expired news file: {filename}")