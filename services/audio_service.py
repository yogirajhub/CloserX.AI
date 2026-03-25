# import base64
# import io
# import audioop
# from pydub import AudioSegment
# from gtts import gTTS
# import speech_recognition as sr

# def twilio_to_text(raw_mulaw_bytes: bytes) -> str:
#     """Twilio ke raw audio bytes ko Text me convert karta hai (STT)"""
#     try:
#         pcm_data = audioop.ulaw2lin(raw_mulaw_bytes, 2)
#         audio_segment = AudioSegment(data=pcm_data, sample_width=2, frame_rate=8000, channels=1)
#         wav_io = io.BytesIO()
#         audio_segment.export(wav_io, format="wav")
#         wav_io.seek(0)
        
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(wav_io) as source:
#             audio_data = recognizer.record(source)
#             return recognizer.recognize_google(audio_data, language='en-IN')
            
#     except sr.UnknownValueError:
#         return ""
#     except sr.RequestError as e:
#         print(f"STT: Google API Error - {e}")
#         return ""
#     except Exception as e:
#         print(f"STT: System Error - {e}")
#         return ""

# def text_to_twilio(text: str) -> str:
#     """LLM ke text ko Twilio ke audio format me convert karta hai (TTS)"""
#     tts = gTTS(text=text, lang='en')
#     mp3_io = io.BytesIO()
#     tts.write_to_fp(mp3_io)
#     mp3_io.seek(0)
    
#     audio_segment = AudioSegment.from_file(mp3_io, format="mp3")
#     audio_segment = audio_segment.set_frame_rate(8000).set_channels(1).set_sample_width(2)
#     pcm_data = audio_segment.raw_data
    
#     mulaw_data = audioop.lin2ulaw(pcm_data, 2)
#     return base64.b64encode(mulaw_data).decode('utf-8')


import base64
import io
import audioop
import time
import random
import re
from pydub import AudioSegment
import speech_recognition as sr
import edge_tts
from logger import get_logger

logger = get_logger(__name__)

FILLER_POOL = [
    "okay",
    "right",
    "hmm",
    "got it",
    "let me check",
    "uh",
]

INDIAN_POLITE_PHRASES = [
    "Sure, let me help you with that.",
    "Just a moment please.",
    "I understand what you're saying.",
]

def twilio_to_text(raw_mulaw_bytes: bytes) -> str:
    """Twilio ke raw audio bytes ko Text me convert karta hai (STT)"""
    try:
        pcm_data = audioop.ulaw2lin(raw_mulaw_bytes, 2)
        audio_segment = AudioSegment(data=pcm_data, sample_width=2, frame_rate=8000, channels=1)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        
        # 🔥 THE ULTIMATE DEBUGGER: Ye har aawaz ko PC me save kar dega
        with open("debug_user_audio.wav", "wb") as f:
            f.write(wav_io.getvalue())
        logger.info("💾 User's voice chunk saved as 'debug_user_audio.wav' in your folder. Play it to hear what AI heard!")

        wav_io.seek(0)
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language='en-IN')
            
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        logger.error(f"STT: Google API Error - {e}")
        return ""
    except Exception as e:
        logger.error(f"STT: System Error - {e}")
        return ""
async def text_to_twilio(text: str) -> str:
    """Edge-TTS se Premium Human-Like Voice Generate Karta hai"""
    # 🛑 Safety net: Empty text hone par crash hone se bachaye
    clean_text = text.replace(",", "").replace(".", "").replace("?", "").replace("!", "").strip()
    if not clean_text:
        return ""
        
    try:
        # VOICE_MODEL: Neerja (Indian Female). Thodi speed (-5%) aur pitch (-2Hz) kam ki hai naturally sound karne ke liye.
        communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural", rate="-5%", pitch="-2Hz")
        audio_data = bytearray()
        
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])
                
        if not audio_data:
            return ""

        # MP3 bytes ko Twilio 8000Hz Mulaw mein convert karna
        mp3_io = io.BytesIO(audio_data)
        audio_segment = AudioSegment.from_file(mp3_io, format="mp3")
        audio_segment = audio_segment.set_frame_rate(8000).set_channels(1).set_sample_width(2)
        pcm_data = audio_segment.raw_data
        
        mulaw_data = audioop.lin2ulaw(pcm_data, 2)
        return base64.b64encode(mulaw_data).decode('utf-8')
        
    except Exception as e:
        logger.error(f"TTS Error in text_to_twilio: {e}")
        return ""


def _escape_ssml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def create_human_voice_payload(
    response_text: str,
    personality: str = "support",
    urgency: str = "normal",
) -> dict:
    """
    Build a speech payload with:
    - ssml: Rich prosody version
    - plain_text: Conversational version
    - params: Voice tuning suggestions
    """
    text = (response_text or "").strip()
    if not text:
        text = "Okay, just a moment please."

    lead_fillers = ["okay", "right", "hmm", "got it"]
    if random.random() < 0.35 and not text.lower().startswith(tuple(lead_fillers)):
        text = f"{random.choice(lead_fillers)}, {text}"

    # Add slight hesitations in long replies to avoid robotic flow.
    if len(text.split()) > 15 and random.random() < 0.4:
        text = re.sub(r", ", ", uh, ", text, count=1)

    if urgency == "high":
        rate = "+4%"
        pitch = "+1Hz"
        break_time = "180ms"
    elif urgency == "low":
        rate = "-4%"
        pitch = "-1Hz"
        break_time = "320ms"
    else:
        rate = "-1%"
        pitch = "-1Hz"
        break_time = "260ms"

    personality_hint = "warm and professional" if personality == "support" else "neutral"
    escaped = _escape_ssml(text)
    ssml = (
        "<speak version='1.0' xml:lang='en-IN'>"
        "<voice name='en-IN-NeerjaNeural'>"
        f"<prosody rate='{rate}' pitch='{pitch}'>"
        f"<emphasis level='moderate'>{escaped}</emphasis>"
        f"<break time='{break_time}'/>"
        "</prosody>"
        "</voice>"
        "</speak>"
    )

    return {
        "ssml": ssml,
        "plain_text": text,
        "params": {
            "voice": "en-IN-NeerjaNeural",
            "rate": rate,
            "pitch": pitch,
            "pause_after_sentence": break_time,
            "tone": personality_hint,
        },
    }


async def text_to_twilio_dynamic(
    text: str,
    urgency: str = "normal",
) -> tuple[str, dict]:
    """
    TTS wrapper with slight random prosody variation per chunk.
    Returns (base64_mulaw_audio, tuning_params).
    """
    text = (text or "").strip()
    if not text:
        return "", {}

    if urgency == "high":
        base_rate = 2
        base_pitch = 1
    elif urgency == "low":
        base_rate = -4
        base_pitch = -1
    else:
        base_rate = -2
        base_pitch = -1

    rate_value = base_rate + random.randint(-2, 2)
    pitch_value = base_pitch + random.randint(-1, 1)
    rate = f"{rate_value:+d}%"
    pitch = f"{pitch_value:+d}Hz"

    try:
        communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural", rate=rate, pitch=pitch)
        audio_data = bytearray()
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data.extend(chunk["data"])

        if not audio_data:
            return "", {"rate": rate, "pitch": pitch}

        mp3_io = io.BytesIO(audio_data)
        audio_segment = AudioSegment.from_file(mp3_io, format="mp3")
        audio_segment = audio_segment.set_frame_rate(8000).set_channels(1).set_sample_width(2)
        pcm_data = audio_segment.raw_data
        mulaw_data = audioop.lin2ulaw(pcm_data, 2)
        return base64.b64encode(mulaw_data).decode("utf-8"), {"rate": rate, "pitch": pitch}
    except Exception as e:
        logger.error(f"TTS Dynamic Error: {e}")
        return await text_to_twilio(text), {"rate": "-2%", "pitch": "-1Hz"}