# import base64
# import io
# import audioop
# from pydub import AudioSegment
# from gtts import gTTS
# import speech_recognition as sr

# def twilio_to_text(raw_mulaw_bytes: bytes) -> str:
#     """Twilio ke raw audio bytes ko Text me convert karta hai (STT)"""
#     try:
#         # Base64 decode yahan se hata diya hai kyunki main.py already kar raha hai
#         pcm_data = audioop.ulaw2lin(raw_mulaw_bytes, 2)
        
#         audio_segment = AudioSegment(
#             data=pcm_data, sample_width=2, frame_rate=8000, channels=1
#         )
#         wav_io = io.BytesIO()
#         audio_segment.export(wav_io, format="wav")
#         wav_io.seek(0)
        
#         recognizer = sr.Recognizer()
#         with sr.AudioFile(wav_io) as source:
#             audio_data = recognizer.record(source)
#             return recognizer.recognize_google(audio_data, language='en-IN')
            
#     except sr.UnknownValueError:
#         print("STT: Silence or unclear audio detected.")
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
from pydub import AudioSegment
from gtts import gTTS
import speech_recognition as sr

def twilio_to_text(raw_mulaw_bytes: bytes) -> str:
    """Twilio ke raw audio bytes ko Text me convert karta hai (STT)"""
    try:
        pcm_data = audioop.ulaw2lin(raw_mulaw_bytes, 2)
        audio_segment = AudioSegment(data=pcm_data, sample_width=2, frame_rate=8000, channels=1)
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)
        
        recognizer = sr.Recognizer()
        with sr.AudioFile(wav_io) as source:
            audio_data = recognizer.record(source)
            return recognizer.recognize_google(audio_data, language='en-IN')
            
    except sr.UnknownValueError:
        return ""
    except sr.RequestError as e:
        print(f"STT: Google API Error - {e}")
        return ""
    except Exception as e:
        print(f"STT: System Error - {e}")
        return ""

def text_to_twilio(text: str) -> str:
    """LLM ke text ko Twilio ke audio format me convert karta hai (TTS)"""
    tts = gTTS(text=text, lang='en')
    mp3_io = io.BytesIO()
    tts.write_to_fp(mp3_io)
    mp3_io.seek(0)
    
    audio_segment = AudioSegment.from_file(mp3_io, format="mp3")
    audio_segment = audio_segment.set_frame_rate(8000).set_channels(1).set_sample_width(2)
    pcm_data = audio_segment.raw_data
    
    mulaw_data = audioop.lin2ulaw(pcm_data, 2)
    return base64.b64encode(mulaw_data).decode('utf-8')