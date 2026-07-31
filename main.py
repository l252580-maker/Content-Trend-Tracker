import customtkinter as ctk
from tkinter import messagebox
from tabulate import tabulate
from pathlib import Path
import threading
import time
from datetime import date

# Original imports
from src.api import fetchNewsForAllTopics
from src.api import extractArticleInfo
from src.api import storeNews
from src.analyzer import loadNewsForTopic
from src.analyzer import cleanArticles
from src.analyzer import calculateRelevanceScore
from src.analyzer import rankTopics
from src.analyzer import loadAlreadyCoveredTopics
from src.analyzer import filterOutCoveredTopics
from src.analyzer import generateRecommendations
from src.history import searchHistory
from src.ai import GeminiService

# --- ORIGINAL CORE LOGIC (Untouched) ---

def addNewTopic(topic):
    from datetime import date
    filepath = Path("data/already_covered.csv")
    if not filepath.exists() or filepath.stat().st_size == 0:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as covered:
            covered.write("Topic,Date\n")
            
    with open(filepath, "a", encoding="utf-8") as covered:
        covered.write(f"{topic},{date.today()}\n")

def callExtractArticleInfo(news):
    for topic, articles in news.items():
        clean_arts = []
        for article in articles:
            article_info = extractArticleInfo(article)
            clean_arts.append(article_info)
        storeNews(topic, clean_arts)

def analyzeNews(target_topics=None):
    import time
    news = Path("data/news")
    topics_scores = {}
    
    yield "Starting analysis..."

    if target_topics is None:
        target_topics = load_interest_topics()
    
    target_files = []
    if target_topics:
        for t in target_topics:
            p = news / f"{t}.csv"
            if p.exists():
                target_files.append(p)

    if not target_files and news.exists():
        target_files = [f for f in news.iterdir() if f.is_file() and f.suffix == ".csv"]

    if not target_files:
        yield "No topic news data available to analyze."
        sorted_topics = rankTopics(topics_scores)
        yield sorted_topics
        return
    
    for topic_csv in target_files:
        topic = topic_csv.stem
        articles = loadNewsForTopic(topic)
        yield f"Loaded: {len(articles)} articles for {topic}"

        cleaned_arts = cleanArticles(articles)
        yield f"Cleaned: {len(cleaned_arts)} articles for {topic}"
        yield f"Calculating relevance score for {topic}..."

        # Sample top 15 most recent articles to avoid payload bloat (>250k chars) & API 429 quota exhaustion
        recent_arts = cleaned_arts[:15]

        trend_analyzer = GeminiService()
        ai_score = trend_analyzer.analyze_trend(topic, recent_arts)
        
        if ai_score > 0:
            topics_scores[topic] = ai_score
        else:
            # Fallback to algorithmic relevance score if AI API is rate-limited or fails (0.0)
            algo_score = min(100.0, calculateRelevanceScore(cleaned_arts) / 10.0)
            topics_scores[topic] = round(algo_score, 2)
            yield f"  ℹ Used algorithmic fallback score ({topics_scores[topic]}) for {topic} (AI API limit)"
            
        time.sleep(0.05)  # Minimal pacing delay
        
    sorted_topics = rankTopics(topics_scores)
    yield sorted_topics


# --- SECURE TOPICS FILE I/O HELPERS ---

def load_interest_topics():
    """Safely read topic list from data/topics.csv (excluding header)."""
    filepath = Path("data/topics.csv")
    if not filepath.exists():
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("Topic\n")
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.read().splitlines()
        if not lines:
            return []
        topics = [line.strip() for line in lines[1:] if line.strip()]
        return topics

def save_interest_topics(topics):
    """Safely rewrite data/topics.csv with header and unique sanitized topics."""
    filepath = Path("data/topics.csv")
    filepath.parent.mkdir(parents=True, exist_ok=True)
    unique_topics = []
    seen = set()
    for t in topics:
        t_clean = t.strip()
        if t_clean and t_clean.lower() not in seen:
            seen.add(t_clean.lower())
            unique_topics.append(t_clean)
            
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("Topic\n")
        for t in unique_topics:
            f.write(f"{t}\n")
    return unique_topics


# --- MODERN EMERALD DESIGN SYSTEM ---
BG_DEEP = "#070c0a"              # Dark Obsidian Emerald background
BG_SURFACE = "#0f1714"           # Elevated panel surface background
BG_CARD = "#15221d"              # Container / Card surface
BG_CARD_HOVER = "#1c2e28"        # Interactive card hover highlight
BORDER_COLOR = "#1e332a"         # Crisp border separation
BORDER_ACCENT = "#10b981"        # Highlight border focus

EMERALD_PRIMARY = "#10b981"      # Modern Vibrant Emerald Accent
EMERALD_HOVER = "#059669"        # Deep Emerald Hover
EMERALD_MUTED = "#064e3b"        # Soft badge fill
EMERALD_GLOW = "#34d399"         # Glowing high-contrast emerald text
EMERALD_SUBTLE = "#022c22"       # Dark tint fill

TEXT_MAIN = "#f3f4f6"            # High contrast primary text
TEXT_MUTED = "#9ca3af"           # Secondary label text
TEXT_DIM = "#6b7280"             # Subtle timestamp / footer text
ACCENT_RED = "#ef4444"           # Error notification tint

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")


class ContentTrendTrackerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Content Trend Tracker • Emerald Edition")
        self.geometry("1180x760")
        self.minsize(980, 650)
        self.configure(fg_color=BG_DEEP)
        
        self.recommendations = []
        self.covered = []
        self.is_analyzing = False
        
        # Configure layout root grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Build UI Architecture
        self._build_sidebar()
        self._build_main_container()
        
        # Default view
        self.show_view("dashboard")
        self._load_initial_stats()

    # =========================================================================
    # SIDEBAR NAVIGATION
    # =========================================================================
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self, 
            width=260, 
            corner_radius=0, 
            fg_color=BG_SURFACE, 
            border_width=1, 
            border_color=BORDER_COLOR
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        # Brand Header Section
        self.brand_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.brand_frame.grid(row=0, column=0, padx=22, pady=(28, 20), sticky="ew")
        
        self.logo_badge = ctk.CTkLabel(
            self.brand_frame, 
            text="⚡ TREND TRACKER", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=EMERALD_GLOW,
            anchor="w"
        )
        self.logo_badge.pack(anchor="w")

        self.subtitle_label = ctk.CTkLabel(
            self.brand_frame,
            text="AI Content Intelligence Engine",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        self.subtitle_label.pack(anchor="w", pady=(2, 0))

        # Primary Run Pipeline Hero Button
        self.btn_run = ctk.CTkButton(
            self.sidebar, 
            text="⚡ Run Analysis Pipeline", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=EMERALD_PRIMARY, 
            hover_color=EMERALD_HOVER,
            text_color="#04120c",
            corner_radius=10,
            height=44,
            command=self.run_analysis
        )
        self.btn_run.grid(row=1, column=0, padx=18, pady=(0, 20), sticky="ew")

        # Navigation Action Button Items
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊 Overview Dashboard"),
            ("recommendations", "🎯 Recommendations"),
            ("topics", "🏷️ Topics of Interest"),
            ("covered", "📋 Covered Topics"),
            ("search", "🔍 Search Archive"),
            ("mark", "✔ Mark Topic Covered"),
        ]

        for idx, (view_key, label_text) in enumerate(nav_items, start=2):
            btn = ctk.CTkButton(
                self.sidebar, 
                text=label_text, 
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), 
                fg_color="transparent", 
                text_color=TEXT_MUTED, 
                hover_color=BG_CARD_HOVER, 
                corner_radius=10, 
                height=40, 
                anchor="w",
                command=lambda k=view_key: self.show_view(k)
            )
            btn.grid(row=idx, column=0, padx=14, pady=3, sticky="ew")
            self.nav_buttons[view_key] = btn

        # Sidebar Footer
        self.footer_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.footer_frame.grid(row=9, column=0, padx=20, pady=20, sticky="s")

        self.status_indicator = ctk.CTkLabel(
            self.footer_frame, 
            text="🟢 Engine Ready", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), 
            text_color=EMERALD_GLOW
        )
        self.status_indicator.pack(anchor="w")

        self.version_label = ctk.CTkLabel(
            self.footer_frame, 
            text="v2.0 • Emerald Modern GUI", 
            font=ctk.CTkFont(family="Segoe UI", size=10), 
            text_color=TEXT_DIM
        )
        self.version_label.pack(anchor="w", pady=(2, 0))

    # =========================================================================
    # MAIN CONTENT PANELS CONTAINER
    # =========================================================================
    def _build_main_container(self):
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.grid(row=0, column=1, sticky="nsew", padx=32, pady=28)
        self.main_container.grid_rowconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(0, weight=1)

        # Dictionary of Views
        self.views = {}
        self.views["dashboard"] = self._create_dashboard_view()
        self.views["recommendations"] = self._create_recommendations_view()
        self.views["topics"] = self._create_topics_view()
        self.views["covered"] = self._create_covered_view()
        self.views["search"] = self._create_search_view()
        self.views["mark"] = self._create_mark_view()

    def show_view(self, view_name):
        """Switch active view tab and update sidebar highlights."""
        for name, frame in self.views.items():
            if name == view_name:
                frame.grid(row=0, column=0, sticky="nsew")
            else:
                frame.grid_forget()

        for name, btn in self.nav_buttons.items():
            if name == view_name:
                btn.configure(fg_color=BG_CARD, text_color=EMERALD_GLOW)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_MUTED)

        if view_name == "topics":
            self._refresh_topics_list()
        elif view_name == "covered":
            self._refresh_covered_list()

    # =========================================================================
    # VIEW 1: DASHBOARD
    # =========================================================================
    def _create_dashboard_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        view.grid_rowconfigure(2, weight=1)
        view.grid_columnconfigure(0, weight=1)

        # Top Header
        header = ctk.CTkLabel(
            view, 
            text="Analytics & System Console", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 16))

        # Metrics Stat Cards Container (3 Cards Grid)
        stats_frame = ctk.CTkFrame(view, fg_color="transparent")
        stats_frame.grid(row=1, column=0, sticky="ew", pady=(0, 20))
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Card 1: Top Recommendations Count
        self.card_rec = ctk.CTkFrame(stats_frame, fg_color=BG_SURFACE, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        self.card_rec.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        ctk.CTkLabel(self.card_rec, text="🎯 ACTIVE RECOMMENDATIONS", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_stat_rec = ctk.CTkLabel(self.card_rec, text="0", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), text_color=EMERALD_GLOW)
        self.lbl_stat_rec.pack(anchor="w", padx=16, pady=(0, 14))

        # Card 2: Covered Topics Count
        self.card_cov = ctk.CTkFrame(stats_frame, fg_color=BG_SURFACE, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        self.card_cov.grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkLabel(self.card_cov, text="📋 TOTAL TOPICS COVERED", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_stat_cov = ctk.CTkLabel(self.card_cov, text="0", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), text_color=TEXT_MAIN)
        self.lbl_stat_cov.pack(anchor="w", padx=16, pady=(0, 14))

        # Card 3: Monitored Topics Count
        self.card_topics_count = ctk.CTkFrame(stats_frame, fg_color=BG_SURFACE, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        self.card_topics_count.grid(row=0, column=2, padx=(10, 0), sticky="ew")
        ctk.CTkLabel(self.card_topics_count, text="🏷️ MONITORED TOPICS", font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"), text_color=TEXT_MUTED).pack(anchor="w", padx=16, pady=(14, 2))
        self.lbl_stat_topics = ctk.CTkLabel(self.card_topics_count, text="0", font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"), text_color=EMERALD_PRIMARY)
        self.lbl_stat_topics.pack(anchor="w", padx=16, pady=(0, 14))

        # Console Container Card
        console_card = ctk.CTkFrame(view, fg_color=BG_SURFACE, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        console_card.grid(row=2, column=0, sticky="nsew")
        console_card.grid_rowconfigure(1, weight=1)
        console_card.grid_columnconfigure(0, weight=1)

        # Progress bar banner
        self.progress_bar = ctk.CTkProgressBar(console_card, fg_color=BG_CARD, progress_color=EMERALD_PRIMARY, height=4, corner_radius=0)
        self.progress_bar.grid(row=0, column=0, sticky="ew")
        self.progress_bar.set(0)

        # Terminal Output Box
        self.textbox = ctk.CTkTextbox(
            console_card, 
            font=ctk.CTkFont(family="Cascadia Code", size=12),
            fg_color="transparent",
            text_color=TEXT_MAIN,
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=EMERALD_PRIMARY,
            wrap="word",
            border_width=0
        )
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=18, pady=16)
        self.write_output("⚡ System Initialized.\nClick 'Run Analysis Pipeline' to pull current topics and run Gemini scoring model.")

        return view

    # =========================================================================
    # VIEW 2: RECOMMENDATIONS (Visual Cards)
    # =========================================================================
    def _create_recommendations_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        view.grid_rowconfigure(1, weight=1)
        view.grid_columnconfigure(0, weight=1)

        # Header bar
        header_frame = ctk.CTkFrame(view, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 16))
        header_frame.grid_columnconfigure(0, weight=1)

        title = ctk.CTkLabel(
            header_frame, 
            text="🎯 Recommended Topics", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        title.grid(row=0, column=0, sticky="w")

        subtitle = ctk.CTkLabel(
            header_frame, 
            text="Ranked high-trend topics ready for content creation", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        subtitle.grid(row=1, column=0, sticky="w")

        # Scrollable Cards Area
        self.rec_scroll = ctk.CTkScrollableFrame(
            view, 
            fg_color="transparent", 
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=EMERALD_PRIMARY
        )
        self.rec_scroll.grid(row=1, column=0, sticky="nsew")
        self.rec_scroll.grid_columnconfigure(0, weight=1)

        self._render_empty_rec_placeholder()
        return view

    def _render_empty_rec_placeholder(self):
        for widget in self.rec_scroll.winfo_children():
            widget.destroy()

        placeholder = ctk.CTkFrame(self.rec_scroll, fg_color=BG_SURFACE, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        placeholder.pack(fill="x", pady=20, padx=10)
        
        lbl = ctk.CTkLabel(
            placeholder, 
            text="No active recommendations generated yet.\nRun the Analysis Pipeline from the sidebar or dashboard to populate recommendations.",
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=TEXT_MUTED,
            justify="center"
        )
        lbl.pack(pady=40, padx=20)

    def _render_recommendation_cards(self):
        for widget in self.rec_scroll.winfo_children():
            widget.destroy()

        if not self.recommendations:
            self._render_empty_rec_placeholder()
            return

        # Find max score for relative progress scaling
        max_score = max([rec.score for rec in self.recommendations]) if self.recommendations else 1.0
        if max_score <= 0: max_score = 1.0

        for idx, rec in enumerate(self.recommendations, start=1):
            card = ctk.CTkFrame(
                self.rec_scroll, 
                fg_color=BG_SURFACE, 
                corner_radius=14, 
                border_width=1, 
                border_color=BORDER_COLOR
            )
            card.pack(fill="x", pady=6, padx=5)
            card.grid_columnconfigure(1, weight=1)

            # Rank Badge Circle
            rank_lbl = ctk.CTkLabel(
                card, 
                text=f"#{idx}", 
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                fg_color=EMERALD_MUTED,
                text_color=EMERALD_GLOW,
                width=42, height=42,
                corner_radius=21
            )
            rank_lbl.grid(row=0, column=0, rowspan=2, padx=16, pady=16)

            # Topic Title & Details
            topic_name = rec.topic.name if hasattr(rec.topic, 'name') else str(rec.topic)
            title_lbl = ctk.CTkLabel(
                card, 
                text=topic_name, 
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
                text_color=TEXT_MAIN,
                anchor="w"
            )
            title_lbl.grid(row=0, column=1, sticky="w", pady=(14, 2))

            # Meter Bar & Score Label
            meter_frame = ctk.CTkFrame(card, fg_color="transparent")
            meter_frame.grid(row=1, column=1, sticky="ew", pady=(0, 14), padx=(0, 16))
            meter_frame.grid_columnconfigure(0, weight=1)

            pbar = ctk.CTkProgressBar(meter_frame, fg_color=BG_CARD, progress_color=EMERALD_PRIMARY, height=8, corner_radius=4)
            pbar.grid(row=0, column=0, sticky="ew", padx=(0, 12))
            pbar.set(min(1.0, max(0.05, float(rec.score) / float(max_score))))

            score_lbl = ctk.CTkLabel(
                meter_frame, 
                text=f"Score: {rec.score:.2f}" if isinstance(rec.score, (float, int)) else f"Score: {rec.score}", 
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                text_color=EMERALD_GLOW
            )
            score_lbl.grid(row=0, column=1, sticky="e")

            # Quick Action Button
            btn_cover = ctk.CTkButton(
                card, 
                text="✔ Mark Covered", 
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color=BG_CARD,
                hover_color=EMERALD_MUTED,
                text_color=TEXT_MAIN,
                corner_radius=8,
                width=120,
                height=34,
                command=lambda t=topic_name: self._direct_mark_covered(t)
            )
            btn_cover.grid(row=0, column=2, rowspan=2, padx=16, pady=16)

    # =========================================================================
    # VIEW 3: TOPICS OF INTEREST MANAGEMENT (New Feature)
    # =========================================================================
    def _create_topics_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        view.grid_rowconfigure(2, weight=1)
        view.grid_columnconfigure(0, weight=1)

        # Header bar
        header = ctk.CTkLabel(
            view, 
            text="🏷️ Topics of Interest", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 4))

        subtitle = ctk.CTkLabel(
            view, 
            text="Manage your active interest topics (persisted safely in data/topics.csv)", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 16))

        # Add New Topic Form Bar
        add_card = ctk.CTkFrame(view, fg_color=BG_SURFACE, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        add_card.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        add_card.grid_columnconfigure(0, weight=1)

        self.entry_new_interest_topic = ctk.CTkEntry(
            add_card, 
            placeholder_text="Enter new interest topic (e.g. Artificial Intelligence, Web Development)...", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=BG_CARD,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=10,
            height=42
        )
        self.entry_new_interest_topic.grid(row=0, column=0, padx=(16, 10), pady=14, sticky="ew")
        self.entry_new_interest_topic.bind("<Return>", lambda e: self._add_interest_topic())

        btn_add_topic = ctk.CTkButton(
            add_card, 
            text="➕ Add Topic", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=EMERALD_PRIMARY,
            hover_color=EMERALD_HOVER,
            text_color="#04120c",
            corner_radius=10,
            height=42,
            width=120,
            command=self._add_interest_topic
        )
        btn_add_topic.grid(row=0, column=1, padx=(0, 16), pady=14)

        # Topics List Container
        self.topics_scroll = ctk.CTkScrollableFrame(
            view, 
            fg_color="transparent",
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=EMERALD_PRIMARY
        )
        self.topics_scroll.grid(row=3, column=0, sticky="nsew")
        self.topics_scroll.grid_columnconfigure(0, weight=1)

        return view

    def _refresh_topics_list(self):
        for widget in self.topics_scroll.winfo_children():
            widget.destroy()

        topics = load_interest_topics()
        self.lbl_stat_topics.configure(text=str(len(topics)))

        if not topics:
            lbl = ctk.CTkLabel(
                self.topics_scroll, 
                text="No topics of interest currently configured.\nAdd a new topic using the input field above.",
                font=ctk.CTkFont(family="Segoe UI", size=13),
                text_color=TEXT_MUTED
            )
            lbl.pack(pady=40)
            return

        for topic_name in topics:
            card = ctk.CTkFrame(self.topics_scroll, fg_color=BG_SURFACE, corner_radius=12, border_width=1, border_color=BORDER_COLOR)
            card.pack(fill="x", pady=4, padx=5)
            card.grid_columnconfigure(0, weight=1)

            t_lbl = ctk.CTkLabel(
                card, 
                text=f"🏷️  {topic_name}", 
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), 
                text_color=TEXT_MAIN, 
                anchor="w"
            )
            t_lbl.grid(row=0, column=0, padx=16, pady=12, sticky="w")

            btn_del = ctk.CTkButton(
                card, 
                text="🗑️ Remove", 
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
                fg_color=BG_CARD,
                hover_color="#7f1d1d",
                text_color="#f87171",
                corner_radius=8,
                width=100,
                height=32,
                command=lambda t=topic_name: self._remove_interest_topic(t)
            )
            btn_del.grid(row=0, column=1, padx=16, pady=12, sticky="e")

    def _add_interest_topic(self):
        new_topic = self.entry_new_interest_topic.get().strip()
        if not new_topic:
            messagebox.showwarning("Input Required", "Please enter a topic name.")
            return

        current_topics = load_interest_topics()
        if any(t.lower() == new_topic.lower() for t in current_topics):
            messagebox.showinfo("Duplicate Topic", f"The topic '{new_topic}' is already in your topics list.")
            return

        current_topics.append(new_topic)
        save_interest_topics(current_topics)
        self.entry_new_interest_topic.delete(0, "end")
        
        self.write_output(f"\n[TOPIC ADDED] Added '{new_topic}' to data/topics.csv successfully.")
        self._refresh_topics_list()
        messagebox.showinfo("Success", f"Added '{new_topic}' to your monitored topics.")

    def _remove_interest_topic(self, topic_name):
        confirm = messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove '{topic_name}' from data/topics.csv?")
        if confirm:
            current_topics = load_interest_topics()
            updated_topics = [t for t in current_topics if t.lower() != topic_name.lower()]
            save_interest_topics(updated_topics)
            
            self.write_output(f"\n[TOPIC REMOVED] Removed '{topic_name}' from data/topics.csv.")
            self._refresh_topics_list()

    # =========================================================================
    # VIEW 4: COVERED TOPICS HISTORY
    # =========================================================================
    def _create_covered_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        view.grid_rowconfigure(2, weight=1)
        view.grid_columnconfigure(0, weight=1)

        # Header bar
        header = ctk.CTkLabel(
            view, 
            text="📋 Coverage History Log", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 12))

        # Filter Entry
        self.entry_covered_filter = ctk.CTkEntry(
            view, 
            placeholder_text="🔍 Filter covered topics history...", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=BG_SURFACE,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=10,
            height=40
        )
        self.entry_covered_filter.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        self.entry_covered_filter.bind("<KeyRelease>", lambda e: self._refresh_covered_list())

        # Scrollable List
        self.covered_scroll = ctk.CTkScrollableFrame(
            view, 
            fg_color="transparent",
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=EMERALD_PRIMARY
        )
        self.covered_scroll.grid(row=2, column=0, sticky="nsew")
        self.covered_scroll.grid_columnconfigure(0, weight=1)

        return view

    def _refresh_covered_list(self):
        for widget in self.covered_scroll.winfo_children():
            widget.destroy()

        self.covered = loadAlreadyCoveredTopics()
        filter_text = self.entry_covered_filter.get().strip().lower()

        if not self.covered or len(self.covered) <= 1:
            lbl = ctk.CTkLabel(self.covered_scroll, text="No covered topic records found.", font=ctk.CTkFont(family="Segoe UI", size=13), text_color=TEXT_MUTED)
            lbl.pack(pady=40)
            return

        records = [line.split(",") for line in self.covered[1:] if line.strip()]

        count = 0
        for rec in records:
            topic_name = rec[0].strip() if len(rec) > 0 else "Unknown"
            cov_date = rec[1].strip() if len(rec) > 1 else "N/A"

            if filter_text and filter_text not in topic_name.lower() and filter_text not in cov_date.lower():
                continue

            count += 1
            row = ctk.CTkFrame(self.covered_scroll, fg_color=BG_SURFACE, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
            row.pack(fill="x", pady=4, padx=5)
            row.grid_columnconfigure(0, weight=1)

            t_lbl = ctk.CTkLabel(row, text=f"•  {topic_name}", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=TEXT_MAIN, anchor="w")
            t_lbl.grid(row=0, column=0, padx=16, pady=12, sticky="w")

            d_lbl = ctk.CTkLabel(row, text=f"📅 {cov_date}", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED)
            d_lbl.grid(row=0, column=1, padx=16, pady=12, sticky="e")

            badge = ctk.CTkLabel(row, text="Covered", font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"), fg_color=EMERALD_MUTED, text_color=EMERALD_GLOW, corner_radius=6, width=70, height=24)
            badge.grid(row=0, column=2, padx=(0, 16), pady=12)

        if count == 0:
            lbl = ctk.CTkLabel(self.covered_scroll, text="No matching records found.", font=ctk.CTkFont(family="Segoe UI", size=13), text_color=TEXT_MUTED)
            lbl.pack(pady=30)

    # =========================================================================
    # VIEW 5: SEARCH ARCHIVE
    # =========================================================================
    def _create_search_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        view.grid_rowconfigure(2, weight=1)
        view.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkLabel(
            view, 
            text="🔍 Search History Archive", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 14))

        # Search Controls Row
        ctrl_frame = ctk.CTkFrame(view, fg_color="transparent")
        ctrl_frame.grid(row=1, column=0, sticky="ew", pady=(0, 16))
        ctrl_frame.grid_columnconfigure(0, weight=1)

        self.entry_search_query = ctk.CTkEntry(
            ctrl_frame, 
            placeholder_text="Type search query term (e.g. Python, AI, Cloud)...", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=BG_SURFACE,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=10,
            height=42
        )
        self.entry_search_query.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.entry_search_query.bind("<Return>", lambda e: self._perform_search())

        btn_do_search = ctk.CTkButton(
            ctrl_frame, 
            text="Search", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=EMERALD_PRIMARY,
            hover_color=EMERALD_HOVER,
            text_color="#04120c",
            corner_radius=10,
            height=42,
            width=110,
            command=self._perform_search
        )
        btn_do_search.grid(row=0, column=1, sticky="e")

        # Results Container Scrollable Frame
        self.search_scroll = ctk.CTkScrollableFrame(
            view, 
            fg_color="transparent",
            scrollbar_button_color=BORDER_COLOR,
            scrollbar_button_hover_color=EMERALD_PRIMARY
        )
        self.search_scroll.grid(row=2, column=0, sticky="nsew")
        self.search_scroll.grid_columnconfigure(0, weight=1)

        return view

    def _perform_search(self):
        for widget in self.search_scroll.winfo_children():
            widget.destroy()

        query = self.entry_search_query.get().strip()
        if not query:
            lbl = ctk.CTkLabel(self.search_scroll, text="Enter a query string above to search covered topics archive.", font=ctk.CTkFont(family="Segoe UI", size=13), text_color=TEXT_MUTED)
            lbl.pack(pady=40)
            return

        self.covered = loadAlreadyCoveredTopics()
        matches = [row for row in self.covered if query.lower() in row.lower()]

        if matches:
            for row_str in matches:
                parts = row_str.split(",")
                t_name = parts[0] if len(parts) > 0 else row_str
                t_date = parts[1] if len(parts) > 1 else "Recorded"

                card = ctk.CTkFrame(self.search_scroll, fg_color=BG_SURFACE, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
                card.pack(fill="x", pady=4, padx=5)
                card.grid_columnconfigure(0, weight=1)

                lbl_title = ctk.CTkLabel(card, text=f"🔍  {t_name}", font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"), text_color=TEXT_MAIN, anchor="w")
                lbl_title.grid(row=0, column=0, padx=16, pady=12, sticky="w")

                lbl_date = ctk.CTkLabel(card, text=f"📅 {t_date}", font=ctk.CTkFont(family="Segoe UI", size=12), text_color=TEXT_MUTED)
                lbl_date.grid(row=0, column=1, padx=16, pady=12, sticky="e")
        else:
            lbl = ctk.CTkLabel(self.search_scroll, text=f"No archive records matching '{query}' found.", font=ctk.CTkFont(family="Segoe UI", size=13), text_color=TEXT_MUTED)
            lbl.pack(pady=40)

    # =========================================================================
    # VIEW 6: MARK TOPIC AS COVERED FORM
    # =========================================================================
    def _create_mark_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")
        view.grid_columnconfigure(0, weight=1)

        header = ctk.CTkLabel(
            view, 
            text="✔ Mark Topic as Covered", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=TEXT_MAIN,
            anchor="w"
        )
        header.grid(row=0, column=0, sticky="w", pady=(0, 6))

        subtitle = ctk.CTkLabel(
            view, 
            text="Lock a topic into the covered topics database so future analysis filters it out.", 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=TEXT_MUTED,
            anchor="w"
        )
        subtitle.grid(row=1, column=0, sticky="w", pady=(0, 20))

        # Form Card
        form_card = ctk.CTkFrame(view, fg_color=BG_SURFACE, corner_radius=16, border_width=1, border_color=BORDER_COLOR)
        form_card.grid(row=2, column=0, sticky="ew", pady=10)
        form_card.grid_columnconfigure(0, weight=1)

        input_lbl = ctk.CTkLabel(form_card, text="Topic Identifier Name:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=TEXT_MAIN)
        input_lbl.pack(anchor="w", padx=24, pady=(20, 6))

        self.entry_mark_topic = ctk.CTkEntry(
            form_card, 
            placeholder_text="Enter exact topic name (e.g. quantum_computing)...", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            fg_color=BG_CARD,
            border_color=BORDER_COLOR,
            border_width=1,
            corner_radius=10,
            height=44
        )
        self.entry_mark_topic.pack(fill="x", padx=24, pady=(0, 16))

        btn_submit = ctk.CTkButton(
            form_card, 
            text="✔ Confirm & Save to Covered Database", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            fg_color=EMERALD_PRIMARY,
            hover_color=EMERALD_HOVER,
            text_color="#04120c",
            corner_radius=10,
            height=44,
            command=self._submit_mark_covered
        )
        btn_submit.pack(anchor="w", padx=24, pady=(0, 24))

        return view

    def _submit_mark_covered(self):
        topic_name = self.entry_mark_topic.get().strip()
        if not topic_name:
            messagebox.showwarning("Input Required", "Please enter a topic name.")
            return

        confirm = messagebox.askyesno("Confirm Update", f"Are you sure you want to mark '{topic_name}' as covered?")
        if confirm:
            addNewTopic(topic_name)
            self.entry_mark_topic.delete(0, "end")
            self.write_output(f"\n[UPDATE] Topic '{topic_name}' marked as covered successfully!")
            self._load_initial_stats()
            self._refresh_covered_list()
            messagebox.showinfo("Success", f"Topic '{topic_name}' recorded in covered database.")

    def _direct_mark_covered(self, topic_name):
        confirm = messagebox.askyesno("Confirm Update", f"Are you sure you want to mark '{topic_name}' as covered?")
        if confirm:
            addNewTopic(topic_name)
            self.write_output(f"\n[UPDATE] Topic '{topic_name}' marked as covered successfully!")
            self._load_initial_stats()
            self._render_recommendation_cards()
            self._refresh_covered_list()

    # =========================================================================
    # CORE PIPELINE EXECUTION & UTILITIES
    # =========================================================================
    def write_output(self, text, clear=False):
        """Safely append or clear console log box."""
        if clear:
            self.textbox.delete("0.0", "end")
        self.textbox.insert("end", text + "\n")
        self.textbox.see("end")
        self.update_idletasks()

    def _load_initial_stats(self):
        """Fetch count of covered topics, interest topics, and recommendations for stats cards."""
        try:
            self.covered = loadAlreadyCoveredTopics()
            cov_count = max(0, len(self.covered) - 1) if self.covered else 0
            self.lbl_stat_cov.configure(text=str(cov_count))
        except Exception:
            self.lbl_stat_cov.configure(text="0")

        try:
            topics = load_interest_topics()
            self.lbl_stat_topics.configure(text=str(len(topics)))
        except Exception:
            self.lbl_stat_topics.configure(text="0")

        self.lbl_stat_rec.configure(text=str(len(self.recommendations)))

    def run_analysis(self):
        """Trigger threaded execution of news extraction and trend analysis."""
        if self.is_analyzing:
            return

        topics = load_interest_topics()
        if not topics:
            messagebox.showwarning("No Topics Found", "Your topics.csv is currently empty. Please add topics of interest in the 'Topics of Interest' tab first.")
            self.show_view("topics")
            return

        self.is_analyzing = True
        self.btn_run.configure(state="disabled", text="⏳ Analyzing...")
        self.status_indicator.configure(text="🟡 Running Analysis...", text_color="#f59e0b")
        self.progress_bar.set(0.1)

        self.show_view("dashboard")
        self.write_output("\n==========================================", clear=True)
        self.write_output("⚡ INITIALIZING TREND ANALYSIS PIPELINE")
        self.write_output("==========================================\n")

        # Run pipeline in background thread so GUI remains 100% responsive
        threading.Thread(target=self._async_pipeline_worker, daemon=True).start()

    def _async_pipeline_worker(self):
        try:
            topics = load_interest_topics()
            self.after(0, self.write_output, f"[1/3] Reading {len(topics)} target topics from data/topics.csv...")
            
            news = {}
            from src.api import fetchNewsForTopic
            for idx, topic in enumerate(topics, start=1):
                self.after(0, self.write_output, f"  ↳ [{idx}/{len(topics)}] Fetching news for '{topic}'...")
                articles = fetchNewsForTopic(topic)
                news[topic] = articles
                self.after(0, self.write_output, f"     Fetched {len(articles)} articles.")
                time.sleep(0.1)
            
            self.after(0, self.write_output, "[2/3] Extracting and storing article metadata...")
            callExtractArticleInfo(news)
            
            self.after(0, self.write_output, "[3/3] Running Gemini AI trend scoring engine...")
            analyzer_gen = analyzeNews(topics)
            sorted_topics = None

            for step in analyzer_gen:
                if isinstance(step, str):
                    self.after(0, self.write_output, f"  ↳ {step}")
                else:
                    sorted_topics = step
            
            self.covered = loadAlreadyCoveredTopics()
            filtered = filterOutCoveredTopics(sorted_topics, self.covered)
            
            self.recommendations = generateRecommendations(filtered, 5)

            # Schedule UI update on main thread
            self.after(0, self._on_pipeline_success)

        except Exception as e:
            self.after(0, self._on_pipeline_error, str(e))

    def _on_pipeline_success(self):
        self.is_analyzing = False
        self.btn_run.configure(state="normal", text="⚡ Run Analysis Pipeline")
        self.status_indicator.configure(text="🟢 Engine Ready", text_color=EMERALD_GLOW)
        self.progress_bar.set(1.0)

        self.write_output("\n[SUCCESS] Pipeline executed successfully!")
        self.write_output(f"Generated {len(self.recommendations)} high-scoring recommendations.")
        self.write_output("Switching to Recommendations tab...")

        self._load_initial_stats()
        self._render_recommendation_cards()
        self.show_view("recommendations")

    def _on_pipeline_error(self, err_msg):
        self.is_analyzing = False
        self.btn_run.configure(state="normal", text="⚡ Run Analysis Pipeline")
        self.status_indicator.configure(text="🔴 Error Occurred", text_color=ACCENT_RED)
        self.progress_bar.set(0)

        self.write_output(f"\n[ERROR] Pipeline failed with exception: {err_msg}")
        messagebox.showerror("Pipeline Exception", f"An error occurred during execution:\n{err_msg}")

    # Legacy method compatibility wrappers
    def view_recommendations(self):
        self.show_view("recommendations")

    def view_covered(self):
        self.show_view("covered")
        self._refresh_covered_list()

    def search_topics(self):
        self.show_view("search")

    def mark_as_covered(self):
        self.show_view("mark")


if __name__ == "__main__":
    app = ContentTrendTrackerGUI()
    app.mainloop()