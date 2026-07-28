def build_trend_analysis_prompt(topic, articles):
    """
    Build the prompt for AI trend analysis.

    Args:
        topic (str): Topic being analyzed.
        articles (list): Related news articles.

    Returns:
        str
    """
    if not articles:
        return f"No articles for the topic '{topic}'."

    articleLines = []
    for article in articles:
        title = article.get("title") or "No title"
        description = article.get("description") or "No description available"
        publishedAt = article.get("published_at") or "Unknown date"

        articleLines.append(
            f"- Headline: {title}\n  Description: {description}\n  Published: {publishedAt}"
        )

    articlesText = "\n".join(articleLines)

    prompt = prompt = f"""Rate how strongly "{topic}" is trending based on these news articles.

    Articles:
    {articlesText}

    Consider coverage volume, recency, and tone.

    Return ONLY JSON:
    {{
        "score": <0-100>
    }}"""

    return prompt