"""
Multi-language Text-to-Speech (TTS) synthesizer.
Generates spoken agricultural advisories in English, Tamil, and Hindi.
"""
import io
import logging
from typing import Optional
from gtts import gTTS

logger = logging.getLogger(__name__)

LANG_CODES = {
    'en': 'en',
    'ta': 'ta',
    'hi': 'hi'
}

def synthesize_speech(text: str, lang: str = 'en') -> Optional[bytes]:
    """
    Synthesize audio bytes using Google TTS.
    Returns MP3 audio bytes or None if offline.
    """
    if not text.strip():
        return None
        
    gtts_lang = LANG_CODES.get(lang, 'en')
    try:
        tts = gTTS(text=text, lang=gtts_lang, slow=False)
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        return fp.read()
    except Exception as e:
        logger.warning(f"gTTS audio synthesis failed: {e}")
        return None
