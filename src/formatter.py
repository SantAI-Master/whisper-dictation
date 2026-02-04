# src/formatter.py
"""Text formatting using GPT for grammar, punctuation, and structure."""
import logging
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

    def format(self, raw_text: str) -> str:
        """Format raw transcription text.

        Args:
            raw_text: Raw transcription from Whisper

        Returns:
            Formatted text with proper grammar and punctuation
        """
        if not raw_text or not raw_text.strip():
            return ""

        # Select prompt based on mode
        prompt = self.SINGLE_LINE_PROMPT if self._mode == "single-line" else self.DOCUMENT_PROMPT

        logger.debug(f"=== FORMATTER DEBUG ===")
        logger.debug(f"Mode: {self._mode}")
        logger.debug(f"Raw input: {repr(raw_text)}")

        response = self._client.chat.completions.create(
            model="gpt-4o-mini",  # Fast and cheap, good for formatting
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": raw_text},
            ],
            temperature=0.3,  # Low temperature for consistent formatting
            max_tokens=2000,
        )

        result = response.choices[0].message.content.strip()
        logger.debug(f"GPT returned: {repr(result)}")
        logger.debug(f"Contains newlines: {'\\n' in result or '\\r' in result}")

        # CRITICAL FAILSAFE: In single-line mode, programmatically strip ALL newlines
        # GPT sometimes ignores prompt instructions, so we enforce this in code
        if self._mode == "single-line":
            # Replace all types of newlines with a space
            result = result.replace('\r\n', ' ').replace('\n', ' ').replace('\r', ' ')
            # Clean up any double spaces that might result
            while '  ' in result:
                result = result.replace('  ', ' ')
            logger.debug(f"After newline strip: {repr(result)}")

        logger.debug(f"=== END DEBUG ===")
        return result
