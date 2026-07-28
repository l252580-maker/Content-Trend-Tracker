"""
Gemini AI service.

Handles communication with the Gemini API for trend analysis.
"""

from google import genai
from dotenv import load_dotenv
import os
import json
from .prompts import build_trend_analysis_prompt

load_dotenv()


class GeminiService:
    """
    Service responsible for AI-powered trend analysis.
    """

    def __init__(self):
        """
        Initialize the Gemini client.

        TODO:
            - Load API key.
            - Initialize Gemini client.
            - Configure model.
        """
        load_dotenv()

        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = "gemini-3.5-flash-lite"

    def analyze_trend(self, topic, articles):
        if not articles:
            return 0.0

        prompt = build_trend_analysis_prompt(topic, articles)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config={"max_output_tokens": 50}
            )

            raw_text = response.text
            clean_text = raw_text.strip().removeprefix("```json").removesuffix("```").strip()

            try:
                result = json.loads(clean_text)
                return float(result.get("score", 0))

            except json.JSONDecodeError:
                return 0.0

        except Exception as e:
            return 0.0
        