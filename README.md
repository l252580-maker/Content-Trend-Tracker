# Content Trend Tracker

An AI-powered trend discovery, news aggregation, and content recommendation system. **Content Trend Tracker** dynamically monitors industry topics, analyzes media volume and recency, leverages Google Gemini AI for intelligent trend evaluation, and provides content creators with actionable topic recommendations via a modern desktop interface.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [System Architecture](#system-architecture)
- [Directory Structure](#directory-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Environment Configuration](#environment-configuration)
- [Usage Instructions](#usage-instructions)
- [How to Contribute](#how-to-contribute)
- [License](#license)

---

## Overview

Staying ahead of fast-moving industry trends requires constant monitoring of global news outlets and statistical evaluation of topic momentum. **Content Trend Tracker** streamlines this workflow by:

1. **Fetching Live News**: Querying real-time articles for target interest topics using the NewsAPI framework.
2. **AI-Driven Trend Analysis**: Utilizing Google Gemini generative models to evaluate topic momentum and market relevance.
3. **Fallback Scoring Algorithm**: Incorporating an automated mathematical scoring mechanism (recency decay + volume weight) whenever API rate limits occur.
4. **Coverage Tracking**: Maintaining historical records of previously covered topics with auto-expiration (30-day TTL) to avoid duplicate content creation.
5. **Modern Desktop Interface**: Providing a rich, user-friendly GUI built with CustomTkinter for real-time operation and monitoring.

---

## Key Features

- 🌐 **Real-time News Aggregation**: Automated retrieval of breaking news across user-defined interest topics.
- 🤖 **Gemini AI Evaluation**: Deep textual analysis of recent articles using `gemini-3.5-flash-lite`.
- 📊 **Algorithmic Fallback Engine**: Mathematical scoring backup calculating exponential time decay and article density.
- 🛡️ **Deduplication & Expiration Management**: 30-day Time-To-Live (TTL) retention for stored news data and covered topics.
- 🖥️ **CustomTkinter Desktop GUI**: Sleek dark-mode desktop interface for topic management, trend analysis execution, and historical search.
- 📁 **Structured Data Persistence**: Modular CSV storage (`data/news/`, `data/topics.csv`, `data/already_covered.csv`).

---

## System Architecture

```
                       +----------------------+
                       |     NewsAPI.org      |
                       +----------+-----------+
                                  |
                                  v
+------------------+     +--------------------+     +-----------------------+
|  CustomTkinter   | --> |  src/api.py        | --> | Local Storage         |
|  Desktop GUI     |     | (Fetch & Extract)  |     | (data/news/<topic>)   |
+--------+---------+     +--------------------+     +-----------+-----------+
         |                                                      |
         |               +--------------------+                 |
         +-------------> |  src/analyzer.py   | <---------------+
                         |  (Clean & Score)   |
                         +---------+----------+
                                   |
                   +---------------+---------------+
                   |                               |
                   v                               v
        +--------------------+          +--------------------+
        |   src/ai.py        |          | Algorithmic        |
        | (Gemini AI Engine) |          | Fallback Engine    |
        +--------------------+          +--------------------+
                   |                               |
                   +---------------+---------------+
                                   |
                                   v
                        +---------------------+
                        | Ranked Shortlist    |
                        | & Recommendations   |
                        +---------------------+
```

---

## Directory Structure

```
Content Trend Tracker/
├── data/
│   ├── news/                 # Stored raw CSV news articles per topic
│   ├── already_covered.csv   # Historical records of covered topics (30-day TTL)
│   └── topics.csv            # Configured target interest topics
├── scripts/                  # Auxiliary automation scripts
│   ├── extract_article_info.py
│   ├── fetch_news_for_all_topics.py
│   └── fetch_news_for_topic.py
├── src/                      # Core backend modules
│   ├── __init__.py
│   ├── ai.py                 # Gemini AI client integration
│   ├── analyzer.py           # Trend scoring and recommendation engine
│   ├── api.py                # NewsAPI integration and storage
│   ├── history.py            # Coverage tracking and search functionality
│   ├── models.py             # Domain data models (Topic, NewsArticle, Recommendation)
│   ├── prompts.py            # AI prompt engineering templates
│   └── utils.py              # Common helper utilities
├── .env                      # API credential configuration (git-ignored)
├── .gitignore                # Git exclusion rules
├── main.py                   # Desktop application entry point & CustomTkinter GUI
├── requirements.txt          # Python library dependencies
└── README.md                 # Project documentation
```

---

## Prerequisites

Ensure your system meets the following requirements before installation:

- **Python**: Version `3.9` or higher
- **NewsAPI Key**: Required for fetching live news articles ([Register at NewsAPI](https://newsapi.org/))
- **Google Gemini API Key**: Required for AI-powered trend analysis ([Obtain at Google AI Studio](https://aistudio.google.com/))

---

## Installation & Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/your-username/content-trend-tracker.git
   cd content-trend-tracker
   ```

2. **Create and Activate a Virtual Environment**
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
   - **Windows (PowerShell):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\Activate.ps1
     ```

3. **Install Required Dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

## Environment Configuration

Create a `.env` file in the project root directory and define your API keys as follows:

```env
# NewsAPI Authentication Key
NEWS_API_KEY=your_news_api_key_here

# Google Gemini API Key
GEMINI_API_KEY=your_gemini_api_key_here
```

> ⚠️ **Important Security Note:** Never commit your `.env` file or API credentials to public source control. The `.env` file is included in `.gitignore` by default.

---

## Usage Instructions

### Launching the Desktop Application

Run the primary application script to open the CustomTkinter GUI:

```bash
python main.py
```

### Application Features & Workflow

1. **Manage Topics**: Add or remove target search topics directly through the GUI topic management pane.
2. **Fetch News**: Trigger news fetching to pull current articles from NewsAPI into local structured storage (`data/news/`).
3. **Analyze Trends**: Run the trend analyzer to compute relevance scores using Gemini AI (with automatic fallback to algorithmic evaluation).
4. **Review Recommendations**: Inspect prioritized recommendation shortlists filtered against previously covered topics.
5. **Mark Covered Topics**: Select topics that have been created and mark them as covered to log them into `already_covered.csv`.

---

## How to Contribute

We welcome contributions from the community! To maintain code quality, consistency, and clear project structure, please follow the guidelines below.

### Step-by-Step Contribution Guide

#### 1. Fork the Repository
Navigate to the official project repository on GitHub and click the **Fork** button in the top right corner to create your copy of the repository.

#### 2. Clone Your Forked Repository
Clone your fork to your local environment:

```bash
git clone https://github.com/YOUR-USERNAME/content-trend-tracker.git
cd content-trend-tracker
```

Configure the upstream remote to keep your fork up to date:

```bash
git remote add upstream https://github.com/ORIGINAL-OWNER/content-trend-tracker.git
```

#### 3. Create a Feature Branch
Create and switch to a descriptive feature branch before making any changes:

```bash
git checkout -b feature/your-feature-name
```

#### 4. Make Modifications & Verify
- Implement your changes following PEP 8 style guidelines.
- Ensure all modules, logic, and tests pass cleanly without errors.
- Test your changes within the application GUI:
  ```bash
  python main.py
  ```

#### 5. Stage and Commit Changes
Add modified files to the staging area and write a concise, imperative commit message:

```bash
# Check modified files
git status

# Stage specific files
git add path/to/file.py

# Commit with a clear commit message
git commit -m "feat: add support for custom news sorting parameters"
```

#### 6. Push Changes to Your Fork
Push your local branch to your remote GitHub repository:

```bash
git push origin feature/your-feature-name
```

#### 7. Open a Pull Request (PR)
1. Go to your repository fork on GitHub (`https://github.com/YOUR-USERNAME/content-trend-tracker`).
2. Click the **Compare & pull request** button.
3. Provide a clear title and detailed summary of the changes introduced in your PR.
4. Submit the Pull Request for code review!

---
