# src/formatter.py
"""Text formatting using GPT for grammar, punctuation, and structure."""
from openai import OpenAI


class TextFormatter:
    """Formats raw transcription text using GPT."""

    SYSTEM_PROMPT = """You are a transcription formatter. Clean up dictated text while following these rules:

CRITICAL - ORDER PRESERVATION:
- NEVER reorder sentences, phrases, or words
- Keep everything in the EXACT order it was spoken
- If something seems out of order, LEAVE IT - the speaker said it that way intentionally
- Do NOT reorganize for "better flow" or "logical order"

FORMATTING RULES:
- Fix spelling and grammar errors
- Add punctuation (periods, commas, question marks)
- Capitalize appropriately
- Keep text on ONE LINE by default - only add a paragraph break for a clear, explicit topic change
- Do NOT add paragraph breaks for pauses or mid-thought corrections
- Do NOT format as bullet points unless the speaker explicitly says "bullet point" or "list"

PRESERVE EXACTLY:
- Self-corrections ("actually, wait, I meant...")
- Filler words if they add meaning
- The speaker's natural phrasing

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
