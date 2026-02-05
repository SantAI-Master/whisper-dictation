# src/formatter.py
"""Text formatting using GPT for grammar, punctuation, and structure."""
import logging
from typing import Callable, Optional
from openai import OpenAI

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class TextFormatter:
    """Formats raw transcription text using GPT."""

    # Single-line mode: Safe for chat apps - no Enter key presses
    SINGLE_LINE_PROMPT = """You are a transcription formatter. Clean up dictated text.

CRITICAL - NEVER ADD NEWLINES:
- Output must be a SINGLE LINE of text - NO line breaks, NO newlines, NO Enter characters
- Do NOT format as bullet points or lists - keep everything as flowing prose
- Do NOT add paragraph breaks for ANY reason
- If the speaker lists items, separate them with commas or semicolons, NOT line breaks

ORDER PRESERVATION:
- NEVER reorder sentences, phrases, or words
- Keep everything in the EXACT order spoken

FORMATTING:
- Fix spelling and grammar
- Add punctuation (periods, commas, question marks)
- Capitalize appropriately

Return ONLY the formatted text on a single line, nothing else."""

    # Document mode: Allows paragraphs - for emails, docs, etc.
    DOCUMENT_PROMPT = """You are a transcription formatter. Clean up dictated text.

ORDER PRESERVATION:
- NEVER reorder sentences, phrases, or words
- Keep everything in the EXACT order spoken
- If something seems out of order, LEAVE IT - the speaker said it that way

FORMATTING:
- Fix spelling and grammar
- Add punctuation (periods, commas, question marks)
- Capitalize appropriately
- Add paragraph breaks ONLY for clear, explicit topic changes
- Do NOT add paragraph breaks for pauses or mid-thought corrections

Return ONLY the formatted text, nothing else."""

    def __init__(self, api_key: str, mode: str = "single-line"):
        if not api_key:
            raise ValueError("API key is required")
        self._client = OpenAI(api_key=api_key)
        self._mode = mode

    def set_mode(self, mode: str):
        """Change the formatting mode at runtime."""
        self._mode = mode

    def get_mode(self) -> str:
        """Get the current formatting mode."""
        return self._mode

    # Maximum words for quick formatting (skip GPT)
    SHORT_TEXT_THRESHOLD = 15

    def _quick_format(self, text: str) -> str:
        """Quick formatting for short text - skip GPT API call.

        Just capitalizes first letter and ensures proper ending punctuation.
        Whisper output is already clean for short phrases.
        """
        result = text.strip()
        if not result:
            return ""

        # Capitalize first letter
        result = result[0].upper() + result[1:] if len(result) > 1 else result.upper()

        # Ensure ending punctuation
        if result[-1] not in '.!?':
            result += '.'

        return result

    def format(self, raw_text: str, on_token: Optional[Callable[[str], None]] = None) -> str:
        """Format raw transcription text.

        Args:
            raw_text: Raw transcription from Whisper
            on_token: Optional callback for streaming - called with each token as it arrives

        Returns:
            Formatted text with proper grammar and punctuation
        """
        if not raw_text or not raw_text.strip():
            return ""

        logger.debug(f"=== FORMATTER DEBUG ===")
        logger.debug(f"Mode: {self._mode}")
        logger.debug(f"Raw input: {repr(raw_text)}")

        # OPTIMIZATION: Skip GPT for short text - Whisper output is clean enough
        word_count = len(raw_text.split())
        if word_count <= self.SHORT_TEXT_THRESHOLD:
            logger.debug(f"Short text ({word_count} words) - skipping GPT")
            result = self._quick_format(raw_text)
            if on_token:
                on_token(result)  # Send all at once for short text
            logger.debug(f"Quick format result: {repr(result)}")
            logger.debug(f"=== END DEBUG ===")
            return result

        # Select prompt based on mode
        prompt = self.SINGLE_LINE_PROMPT if self._mode == "single-line" else self.DOCUMENT_PROMPT

        # Use streaming if callback provided
        if on_token:
            return self._format_streaming(raw_text, prompt, on_token)

        # Non-streaming path
        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text},
            ],
            temperature=0.3,
            max_tokens=2000,
        )

        result = response.choices[0].message.content.strip()
        logger.debug(f"GPT returned: {repr(result)}")

        result = self._enforce_single_line(result)
        logger.debug(f"=== END DEBUG ===")
        return result

    def _format_streaming(self, raw_text: str, prompt: str, on_token: Callable[[str], None]) -> str:
        """Stream formatted text token by token for faster perceived response."""
        logger.debug("Using streaming GPT response")

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text},
            ],
            temperature=0.3,
            max_tokens=2000,
            stream=True,
        )

        full_text = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                token = chunk.choices[0].delta.content

                # In single-line mode, replace newlines with spaces on the fly
                if self._mode == "single-line":
                    token = token.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')

                full_text += token
                on_token(token)

        logger.debug(f"Streamed result: {repr(full_text)}")
        logger.debug(f"=== END DEBUG ===")
        return full_text

    def _enforce_single_line(self, result: str) -> str:
        """Strip all newlines in single-line mode."""
        if self._mode == "single-line":
            result = result.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            while '  ' in result:
                result = result.replace('  ', ' ')
            logger.debug(f"After newline strip: {repr(result)}")
        return result
