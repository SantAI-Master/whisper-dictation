# src/formatter.py
"""Text formatting using GPT for grammar, punctuation, and structure."""
from openai import OpenAI


class TextFormatter:
    """Formats raw transcription text using GPT."""

    SYSTEM_PROMPT = """You are a text formatter. Your job is to take raw voice transcription and format it properly:

- Fix grammar and spelling
- Add proper punctuation (periods, commas, question marks, etc.)
- Capitalize appropriately
- Break into paragraphs where natural pauses or topic changes occur
- If the speaker lists items, format as bullet points
- Preserve the original meaning exactly - do not add or remove content
- Do not add any commentary or explanations

Return ONLY the formatted text, nothing else."""

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("API key is required")
        self._client = OpenAI(api_key=api_key)

    def format(self, raw_text: str) -> str:
        """Format raw transcription text.

        Args:
            raw_text: Raw transcription from Whisper

        Returns:
            Formatted text with proper grammar, punctuation, paragraphs
        """
        if not raw_text or not raw_text.strip():
            return ""

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap, good for formatting
            messages=[
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": raw_text},
            ],
            temperature=0.3,  # Low temperature for consistent formatting
            max_tokens=2000,
        )

        return response.choices[0].message.content.strip()
