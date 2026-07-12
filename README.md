# AI-Powered Content Trend Tracker

## Overview

The AI-Powered Content Trend Tracker is a command-line application designed to help a solo content creator identify trending news topics for future content. The system collects recent news related to predefined topics, analyzes their relevance, checks whether they have already been covered, and recommends the most suitable topics for new content.

The primary goal of this project is to reduce the time spent manually searching for news, minimize repeated content, and improve the timing of published posts.

---

## Problem Statement

Content creators often spend significant time searching multiple news sources before deciding what to post. This manual process is repetitive and may lead to missed trends or repeated coverage of similar topics.

This application automates the research process by monitoring predefined topics, analyzing current news activity, and maintaining a history of previously covered content.

---

## Objectives

- Fetch recent news for selected topics.
- Analyze which topics are currently trending.
- Maintain a history of previously covered topics.
- Recommend the most relevant topics for future content.
- Reduce manual research time.
- Minimize duplicate content suggestions.

---

## Features

- Retrieve recent news using a News API.
- Analyze article frequency and recency.
- Rank topics by relevance.
- Track previously covered topics.
- Display recommendations through a Command-Line Interface (CLI).
- Store project data locally using CSV files.

---

## Technologies Used

- Python
- Requests
- Pandas
- Python-dotenv
- Tabulate
- CSV
- NewsAPI (Free Tier)

---

## Project Structure

```text
Content Trend Tracker/
│
├── data/
│   ├── topics.csv
│   └── already_covered.csv
│
├── src/
│   ├── main.py
│   ├── api.py
│   ├── analyzer.py
│   ├── history.py
│   ├── models.py
│   └── utils.py
│
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── venv/
```

---

## Module Responsibilities

### `main.py`
Acts as the application's entry point. It coordinates the execution of all project modules and controls the overall workflow.

### `api.py`
Handles communication with the News API, sends requests, and retrieves recent news articles.

### `analyzer.py`
Processes collected news data, calculates relevance scores, and ranks topics according to their importance.

### `history.py`
Manages previously covered topics by reading from and writing to `already_covered.csv`.

### `models.py`
Contains data models or classes used throughout the application, such as `Topic`, `NewsArticle`, and `Recommendation`.

### `utils.py`
Provides reusable helper functions, including formatting, validation, and utility operations.

---

## Data Files

### `topics.csv`

Stores the predefined topics that the application monitors.

**Example:**

```csv
Topic
Pakistan
China
India
Russia
Artificial Intelligence
```

### `already_covered.csv`

Maintains a history of topics that have already been published.

**Example:**

```csv
Topic,Date
China-Pakistan Economic Corridor,2026-07-05
US-China Trade Relations,2026-07-08
```

---

## Workflow

```text
Start
  │
  ▼
Load topics from topics.csv
  │
  ▼
Fetch news from News API
  │
  ▼
Process and clean news data
  │
  ▼
Calculate relevance scores
  │
  ▼
Check already_covered.csv
  │
  ▼
Rank topics
  │
  ▼
Display recommendations
  │
  ▼
User marks a topic as covered
  │
  ▼
Update already_covered.csv
  │
  ▼
End
```

---

## Expected Output

The application displays a ranked list of trending topics based on current news activity and previous posting history, allowing the creator to quickly decide what content to produce next.

---

## Future Enhancements

- Web interface using Flask or Streamlit
- AI-generated content suggestions
- Sentiment analysis of news articles
- Topic trend visualization
- Multi-user support
- Automatic content scheduling

---

## Author

**Qazi Rayyan**

FAST National University of Computer and Emerging Sciences (FAST-NUCES)

Semester Project – Data Science Learning Project