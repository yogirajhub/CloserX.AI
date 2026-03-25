# # import base64
# # from fastapi import FastAPI, WebSocket, Request, BackgroundTasks
# # from fastapi.responses import HTMLResponse
# # from fastapi.staticfiles import StaticFiles
# # from fastapi.templating import Jinja2Templates
# # from pydantic import BaseModel
# # import json
# # import os
# # from datetime import datetime

# # from services.llm_service import generate_answer, summarize_call
# # from services.knowledge_base import load_json, answer_question
# # from config import settings
# # from logger import get_logger
# # from twilio.rest import Client
# # from fastapi import WebSocketDisconnect
# # from services.audio_service import twilio_to_text, text_to_twilio
# # import asyncio
# # from datetime import datetime
# # from services.llm_service import generate_call_summary # Naya function import kiya

# # # Calls ka data store karne ke liye (Server restart hone par ye clear ho jayega)
# # # main.py mein apne purane call_history_db = [] ko isse replace kar dein:

# # # Naya Local Storage Logic
# # DB_FILE = "call_history.json"

# # # Jab server start hoga, toh pehle check karega ki kya purani file exist karti hai
# # if os.path.exists(DB_FILE):
# #     with open(DB_FILE, "r") as f:
# #         call_history_db = json.load(f)
# # else:
# #     call_history_db = []

# # def save_to_local_file():
# #     """Ye function list ko json file me permanently save karega"""
# #     with open(DB_FILE, "w") as f:
# #         json.dump(call_history_db, f, indent=4)

# # # Is class ko define karna zaroori hai error hatane ke liye
# # class CallRequest(BaseModel):
# #     phone_number: str
# # logger = get_logger("main")

# # app = FastAPI()
# # app.mount("/static", StaticFiles(directory="static"), name="static")
# # templates = Jinja2Templates(directory="templates")

# # class AnswerPayload(BaseModel):
# #     id: int
# #     answer: str

# # @app.get("/", response_class=HTMLResponse)
# # async def index(request: Request):
# #     return templates.TemplateResponse("index.html", {"request": request})

# # @app.get("/api/unanswered")
# # async def get_unanswered():
# #     return load_json("data/unanswered.json")

# # @app.get("/api/call_history")
# # async def get_call_history():
# #     """Dashboard ko call history bhejne ke liye"""
# #     # [::-1] ka matlab hai list ko reverse karna, taaki sabse nayi call sabse upar dikhe
# #     return {"history": call_history_db[::-1]}

# # @app.post("/api/answer")
# # async def submit_answer(payload: AnswerPayload):
# #     answer_question(payload.id, payload.answer)
# #     return {"status": "success"}

# # # --- TWILIO CALLING LOGIC ---
# # @app.post("/twiml")
# # async def twilio_webhook(request: Request):
# #     """Initial Twilio Webhook to start the WebSocket stream"""
# #     host = settings.NGROK_URL.replace("https://", "")
# #     xml = f"""<?xml version="1.0" encoding="UTF-8"?>
# #     <Response>
# #         <Connect>
# #             <Stream url="wss://{host}/media-stream" />
# #         </Connect>
# #     </Response>"""
# #     return HTMLResponse(content=xml, media_type="application/xml")

# # @app.websocket("/media-stream")
# # async def websocket_endpoint(websocket: WebSocket):
# #     await websocket.accept()
# #     stream_sid = None
# #     call_sid = None  # NAYA CHANGE: Call SID ko track karne ke liye variable add kiya
    
# #     # NAYA BADA CHANGE: Ab hum text nahi, raw audio bytes store karenge
# #     audio_buffer = bytearray()
# #     call_transcript = []
    
# #     try:
# #         while True:
# #             message = await websocket.receive_text()
# #             data = json.loads(message)
            
# #             if data['event'] == 'connected':
# #                 logger.info("Twilio WebSocket Connected Successfully!")

# #             # ... (baaki code)
# #             elif data['event'] == 'start':
# #                 stream_sid = data['start']['streamSid']
# #                 # NAYI LINE: Twilio ka asli Call SID capture karein
# #                 call_sid = data['start'].get('callSid', 'Unknown_Call_SID') 
                
# #                 logger.info(f"Incoming Stream Started: {stream_sid} | Call SID: {call_sid}")
# #                 # ... (baaki greeting wala code)
                
# #                 greeting_text = "Hello, this is CloserX. How can I help you today?"
# #                 call_transcript.append(f"AI: {greeting_text}")
                
# #                 try:
# #                     base64_audio = text_to_twilio(greeting_text)
# #                     await websocket.send_text(json.dumps({
# #                         "event": "media",
# #                         "streamSid": stream_sid,
# #                         "media": {"payload": base64_audio}
# #                     }))
# #                     logger.info("Greeting voice sent to user.")
# #                 except Exception as e:
# #                     logger.error(f"Error converting/sending greeting: {e}")
                
# #             elif data['event'] == 'media':
# #                 # NAYA CHANGE: Pehle Base64 decode karein, phir buffer mein dalein
# #                 chunk_bytes = base64.b64decode(data['media']['payload'])
# #                 audio_buffer.extend(chunk_bytes)
                
# #                 # Twilio 1 second mein 8000 bytes bhejta hai. 32000 = 4 Seconds ki aawaz.
# #                 if len(audio_buffer) > 32000: 
# #                     logger.info("Analyzing user audio chunk...")
                    
# #                     # Bytearray ko normal bytes mein convert karke bhejein
# #                     user_text = twilio_to_text(bytes(audio_buffer))
                    
# #                     # Sliding Window: Aakhiri 1 second (8000 bytes) bachayein taaki word na kate
# #                     audio_buffer = audio_buffer[-8000:] 
                    
# #                     if user_text and user_text.strip():
# #                         logger.info(f"User said: {user_text}")
# #                         call_transcript.append(f"User: {user_text}")
                        
# #                         # Aawaz pakadte hi buffer khali karein
# #                         audio_buffer = bytearray()
                        
# #                         ai_answer = generate_answer(user_text)
# #                         logger.info(f"AI Answer: {ai_answer}")
# #                         call_transcript.append(f"AI: {ai_answer}")
                        
# #                         try:
# #                             ai_audio_base64 = text_to_twilio(ai_answer)
# #                             await websocket.send_text(json.dumps({
# #                                 "event": "media",
# #                                 "streamSid": stream_sid,
# #                                 "media": {"payload": ai_audio_base64}
# #                             }))
# #                             logger.info("AI voice sent back to user.")
# #                         except Exception as e:
# #                             logger.error(f"Error sending AI audio: {e}")
                        
# #             elif data['event'] == 'stop':
# #                 logger.info("Call disconnected.")
# #                 full_conversation = "\n".join(call_transcript)
                
# #                 summary = "User did not speak."
# #                 if len(call_transcript) > 1:
# #                     logger.info("Generating call summary...")
# #                     summary = generate_call_summary(full_conversation)
                
# #                 # NAYA: Call SID ke sath data record karein
# #                 call_record = {
# #                     "call_sid": call_sid,  # Twilio ki unique ID
# #                     "stream_sid": stream_sid,
# #                     "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
# #                     "phone": "Inbound/Outbound Call",
# #                     "summary": summary,
# #                     "transcript": full_conversation
# #                 }
                
# #                 # List me add karein aur turant File me Save kar dein
# #                 call_history_db.append(call_record)
# #                 save_to_local_file() # 🔥 Ye line file banayegi/update karegi
                
# #                 logger.info(f"Call permanently saved to {DB_FILE}")
# #                 break
                
# #     except WebSocketDisconnect:
# #         logger.info("WebSocket disconnected gracefully.")
# #     except Exception as e:
# #         logger.error(f"Error in WebSocket: {e}")
        
# # @app.post("/api/make_call")
# # async def make_outbound_call(payload: CallRequest):
# #     """Dashboard se outbound call initiate karne ke liye"""
# #     try:
# #         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
# #         # Twilio ko batana hai ki call uthne ke baad kya karna hai
# #         # Hum usko apne /twiml endpoint par bhejenge jo WebSocket connect karega
# #         twiml_url = f"{settings.NGROK_URL}/twiml"
        
# #         call = client.calls.create(
# #             to=payload.phone_number,
# #             from_=settings.TWILIO_PHONE_NUMBER,
# #             url=twiml_url
# #         )
# #         logger.info(f"Call initiated successfully. SID: {call.sid}")
# #         return {"status": "success", "message": f"Calling {payload.phone_number}..."}
        
# #     except Exception as e:
# #         logger.error(f"Failed to make call: {e}")
# #         return {"status": "error", "message": str(e)}

# import base64
# import json
# import os
# import io
# import PyPDF2  # NAYI LIBRARY: PDF read karne ke liye
# from datetime import datetime
# from fastapi import FastAPI, WebSocket, Request, UploadFile, File, WebSocketDisconnect
# from fastapi.responses import HTMLResponse, Response
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# from twilio.rest import Client

# from services.llm_service import generate_answer, summarize_call , generate_answer_stream
# from services.knowledge_base import get_unanswered_questions, answer_question, update_document
# from services.audio_service import twilio_to_text, text_to_twilio
# from config import settings
# from logger import get_logger
# import audioop  # Ye aawaz ki volume napne ke kaam aayega

# logger = get_logger("main")
# app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# # --- Local Storage For Call History ---
# DB_FILE = "data/call_history.json"
# os.makedirs("data", exist_ok=True)

# if os.path.exists(DB_FILE):
#     with open(DB_FILE, "r") as f: 
#         call_history_db = json.load(f)
# else:
#     call_history_db = []

# def save_to_local_file():
#     with open(DB_FILE, "w") as f: 
#         json.dump(call_history_db, f, indent=4)

# # --- Models ---
# class CallRequest(BaseModel):
#     phone_number: str

# class AnswerPayload(BaseModel):
#     id: int
#     answer: str

# # --- REST APIs ---
# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.post("/api/upload_doc")
# async def upload_document(file: UploadFile = File(...)):
#     """Upload TXT or PDF document for RAG AI"""
#     try:
#         content = await file.read()
#         text = ""
        
#         # Agar file PDF hai, toh extract text
#         if file.filename.lower().endswith(".pdf"):
#             pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
#             for page in pdf_reader.pages:
#                 extracted = page.extract_text()
#                 if extracted:
#                     text += extracted + "\n"
#         else:
#             # Agar normal txt file hai
#             text = content.decode("utf-8")
            
#         update_document(text)
#         return {"message": f"{file.filename} learned successfully!"}
        
#     except Exception as e:
#         logger.error(f"Upload Error: {e}")
#         return {"status": "error", "message": "Failed to read the file. Please check format."}

# @app.get("/api/unanswered")
# async def get_unanswered():
#     return get_unanswered_questions()

# @app.post("/api/answer")
# async def submit_answer(payload: AnswerPayload):
#     answer_question(payload.id, payload.answer)
#     return {"status": "success"}

# @app.get("/api/call_history")
# async def get_call_history():
#     return {"history": call_history_db[::-1]}

# @app.post("/api/make_call")
# async def make_outbound_call(payload: CallRequest):
#     try:
#         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
#         twiml_url = f"{settings.NGROK_URL}/twiml"
#         call = client.calls.create(to=payload.phone_number, from_=settings.TWILIO_PHONE_NUMBER, url=twiml_url)
#         return {"status": "success", "message": f"Calling {payload.phone_number}...", "call_sid": call.sid}
#     except Exception as e:
#         logger.error(f"Failed to make call: {e}")
#         return {"status": "error", "message": str(e)}

# @app.post("/twiml")
# async def twilio_webhook():
#     host = settings.NGROK_URL.replace("https://", "").replace("http://", "")
#     xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Connect><Stream url="wss://{host}/media-stream" /></Connect></Response>"""
#     return Response(content=xml, media_type="text/xml")

# # --- WEBSOCKET ---
# @app.websocket("/media-stream")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     stream_sid = None
#     call_sid = None 
    
#     # --- SMART VAD VARIABLES ---
#     audio_buffer = bytearray()
#     call_transcript = []
#     is_user_speaking = False
#     silence_count = 0
    
#     # Twilio har 20ms mein audio bhejta hai. 40 packets = 0.8 seconds of silence.
#     SILENCE_LIMIT = 40  
#     # Volume Check Threshold (Agar background noise zyada ho toh isko badha de)
#     VOLUME_THRESHOLD = 500  

#     try:
#         while True:
#             message = await websocket.receive_text()
#             data = json.loads(message)
            
#             if data['event'] == 'start':
#                 stream_sid = data['start']['streamSid']
#                 call_sid = data['start'].get('callSid', 'Unknown_Call_SID') 
#                 logger.info(f"Stream Started: {stream_sid}")
                
#                 greeting_text = "Hello, this is Closer X. How can I help you today?"
#                 call_transcript.append(f"AI: {greeting_text}")
#                 await websocket.send_text(json.dumps({
#                     "event": "media", "streamSid": stream_sid,
#                     "media": {"payload": text_to_twilio(greeting_text)}
#                 }))
                
#             elif data['event'] == 'media':
#                 chunk = base64.b64decode(data['media']['payload'])
                
#                 # Aawaz ki volume (Energy) measure karna
#                 try:
#                     pcm_chunk = audioop.ulaw2lin(chunk, 2)
#                     rms_volume = audioop.rms(pcm_chunk, 2)
#                 except Exception:
#                     rms_volume = 0
                
#                 # Agar volume threshold se zyada hai -> User bol raha hai!
#                 if rms_volume > VOLUME_THRESHOLD:
#                     is_user_speaking = True
#                     silence_count = 0
#                     audio_buffer.extend(chunk)
                
#                 # User bol raha tha, par ab chup ho gaya hai
#                 elif is_user_speaking:
#                     silence_count += 1
#                     audio_buffer.extend(chunk)
                    
#                    # Agar user 0.8 seconds tak chup raha, toh sentence complete maano
#                     if silence_count > SILENCE_LIMIT:
                        
#                         # Barge-in: Twilio ko chup karao
#                         await websocket.send_text(json.dumps({"event": "clear", "streamSid": stream_sid}))
                        
#                         # Audio ko text me convert karo
#                         user_text = twilio_to_text(bytes(audio_buffer))
                        
#                         if user_text and len(user_text.strip()) > 3:
#                             call_transcript.append(f"User: {user_text}")
#                             logger.info(f"User (Complete Sentence): {user_text}")
                            
#                             full_ai_response = ""
                            
#                             # Streaming Loop: LLM ki ek-ek line aayegi aur turant bol di jayegi
#                             for sentence in generate_answer_stream(user_text):
                                
#                                 # Agar I_DONT_KNOW aaya, toh standard reply set karo
#                                 if "I_DONT_KNOW" in sentence:
#                                     from services.knowledge_base import log_unanswered_question
#                                     log_unanswered_question(user_text)
#                                     sentence = "We currently do not have that information, but we will get back to you soon."
                                
#                                 full_ai_response += sentence + " "
#                                 logger.info(f"AI Streaming: {sentence}")
                                
#                                 # Ek line ka audio bana kar Twilio ko bhej do (FAST!)
#                                 await websocket.send_text(json.dumps({
#                                     "event": "media", 
#                                     "streamSid": stream_sid,
#                                     "media": {"payload": text_to_twilio(sentence)}
#                                 }))
                                
#                             call_transcript.append(f"AI: {full_ai_response.strip()}")
                            
#                         # Reset for next sentence
#                         audio_buffer = bytearray()
#                         is_user_speaking = False
#                         silence_count = 0
                
#                 # Agar user kuch nahi bol raha, toh bas thoda sa audio buffer me rakho (Pre-roll)
#                 else:
#                     audio_buffer.extend(chunk)
#                     if len(audio_buffer) > 4000: # Sirf pichle 0.5 second ka record rakho
#                         audio_buffer = audio_buffer[-4000:]
                        
#             elif data['event'] == 'stop':
#                 full_convo = "\n".join(call_transcript)
#                 summary = summarize_call(full_convo) if len(call_transcript) > 1 else "No interaction."
#                 call_history_db.append({
#                     "call_sid": call_sid, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "summary": summary, "transcript": full_convo
#                 })
#                 save_to_local_file()
#                 break
                
#     except WebSocketDisconnect:
#         logger.info("Call disconnected gracefully.")







import base64
import json
import os
import io
import time  
import asyncio  
import PyPDF2  
from datetime import datetime
from fastapi import FastAPI, WebSocket, Request, UploadFile, File, WebSocketDisconnect
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from twilio.rest import Client

from services.llm_service import (
    summarize_call,
    generate_answer_stream,
    detect_intent_for_filler,
    apply_conversational_polish,
)
from services.knowledge_base import get_unanswered_questions, answer_question, update_document
from services.audio_service import (
    twilio_to_text,
    text_to_twilio,
    text_to_twilio_dynamic,
    create_human_voice_payload,
)
from config import settings
from logger import get_logger
import audioop  

logger = get_logger("main")
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Local Storage For Call History ---
DB_FILE = "data/call_history.json"
os.makedirs("data", exist_ok=True)

if os.path.exists(DB_FILE):
    with open(DB_FILE, "r") as f: 
        call_history_db = json.load(f)
else:
    call_history_db = []

def save_to_local_file():
    try:
        with open(DB_FILE, "w") as f: 
            json.dump(call_history_db, f, indent=4)
        logger.info("💾 Call history saved successfully.")
    except Exception as e:
        logger.error(f"❌ Failed to save call history: {e}")

# ==========================================
# 🧠 SMART LOGICAL FILLERS SETUP
# ==========================================
PRE_GENERATED_FILLERS = {}
LAST_VOICE_DESIGN_SAMPLE = {}

@app.on_event("startup")
async def startup_event():
    start_time = time.time()
    logger.info("🚀 Server Starting... Generating Logical Fillers with Edge-TTS...")
    
    fillers_dict = {
        "empathetic": "I see...",        
        "thinking": "Hmm, let me check...",            
        "affirmative": "Right.",         
        "neutral": "Okay."               
    }
    
    for intent, text in fillers_dict.items():
        try:
            tts_start = time.time()
            audio_b64 = await text_to_twilio(text)
            if audio_b64:
                PRE_GENERATED_FILLERS[intent] = audio_b64
                logger.info(f"✅ Filler '{intent}' generated in {time.time() - tts_start:.3f}s")
        except Exception as e:
            logger.error(f"❌ Error generating filler '{intent}': {e}")
            
    logger.info(f"🎉 All Caching complete in {time.time() - start_time:.3f}s!")

    # Build one ready-to-use design sample for dashboard/API testing.
    global LAST_VOICE_DESIGN_SAMPLE
    LAST_VOICE_DESIGN_SAMPLE = create_human_voice_payload(
        "Sure, let me help you with that. Hmm, just a moment please while I check this for you.",
        personality="support",
        urgency="normal",
    )

# --- Models ---
class CallRequest(BaseModel):
    phone_number: str

class AnswerPayload(BaseModel):
    id: int
    answer: str

# --- REST APIs ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/api/upload_doc")
async def upload_document(file: UploadFile = File(...)):
    logger.info(f"📂 Document upload initiated: {file.filename}")
    try:
        content = await file.read()
        text = ""
        if file.filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            text = content.decode("utf-8")
            
        update_document(text)
        logger.info(f"✅ Document '{file.filename}' learned successfully.")
        return {"message": f"{file.filename} learned successfully!"}
    except Exception as e:
        logger.error(f"❌ Document Upload Error: {e}")
        return {"status": "error", "message": "Failed to read the file."}

@app.get("/api/unanswered")
async def get_unanswered():
    return get_unanswered_questions()

@app.post("/api/answer")
async def submit_answer(payload: AnswerPayload):
    answer_question(payload.id, payload.answer)
    return {"status": "success"}

@app.get("/api/call_history")
async def get_call_history():
    return {"history": call_history_db[::-1]}


@app.get("/api/voice_design_sample")
async def voice_design_sample():
    """
    Returns:
      a) sample SSML response
      b) plain text conversational version
      c) voice tuning parameters
    """
    sample = LAST_VOICE_DESIGN_SAMPLE or create_human_voice_payload(
        "Right, I understand what you're saying. Let me check this quickly.",
        personality="support",
        urgency="normal",
    )
    return sample

@app.post("/api/make_call")
async def make_outbound_call(payload: CallRequest):
    logger.info(f"📞 Initiating outbound call to {payload.phone_number}...")
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        twiml_url = f"{settings.NGROK_URL}/twiml"
        call = client.calls.create(to=payload.phone_number, from_=settings.TWILIO_PHONE_NUMBER, url=twiml_url)
        logger.info(f"✅ Call placed! SID: {call.sid}")
        return {"status": "success", "message": f"Calling {payload.phone_number}...", "call_sid": call.sid}
    except Exception as e:
        logger.error(f"❌ Failed to make outbound call: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/twiml")
async def twilio_webhook():
    host = settings.NGROK_URL.replace("https://", "").replace("http://", "")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Connect><Stream url="wss://{host}/media-stream" /></Connect></Response>"""
    return Response(content=xml, media_type="text/xml")

# ==========================================
# 🔌 WEBSOCKET ENGINE (CORE AI AGENT)
# ==========================================
@app.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    stream_sid = None
    call_sid = None 
    
    audio_buffer = bytearray()
    call_transcript = []
    is_user_speaking = False
    silence_count = 0
    noise_count = 0  
    
    ai_speaking_flag = False
    cancel_current_response = False 
    
    # 🎛️ Hyper-Tuned Variables
    SILENCE_LIMIT = 40
    VOLUME_THRESHOLD = 3000 
    BARGE_IN_LIMIT = 15

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data['event'] == 'start':
                stream_sid = data['start']['streamSid']
                call_sid = data['start'].get('callSid', 'Unknown') 
                logger.info(f"🎙️ Stream Connected! Call SID: {call_sid}")
                
                greeting_text = "Hello, this is Closer X. How can I help you today?"
                call_transcript.append(f"AI: {greeting_text}")
                
                ai_speaking_flag = True
                greet_start = time.time()
                greeting_audio_base64 = await text_to_twilio(greeting_text)
                logger.info(f"⏱️ Greeting TTS Generation Latency: {time.time() - greet_start:.3f}s")
                
                if not cancel_current_response and greeting_audio_base64:
                    try:
                        await websocket.send_text(json.dumps({
                            "event": "media", "streamSid": stream_sid,
                            "media": {"payload": greeting_audio_base64}
                        }))
                    except Exception:
                        pass
                ai_speaking_flag = False
                
            elif data['event'] == 'media':
                chunk = base64.b64decode(data['media']['payload'])
                
                try:
                    pcm_chunk = audioop.ulaw2lin(chunk, 2)
                    rms_volume = audioop.rms(pcm_chunk, 2)
                except Exception:
                    rms_volume = 0
                
                # --- 🛑 ECHO-PROOF BARGE-IN ---
                if rms_volume > VOLUME_THRESHOLD:
                    noise_count += 1
                    if noise_count > BARGE_IN_LIMIT:
                        if ai_speaking_flag:
                            logger.warning("🚨 Genuine Barge-in Triggered! Stop AI Voice.")
                            cancel_current_response = True  
                            ai_speaking_flag = False        
                            try:
                                await websocket.send_text(json.dumps({"event": "clear", "streamSid": stream_sid}))
                            except Exception:
                                pass
                        
                        is_user_speaking = True
                        silence_count = 0
                        audio_buffer.extend(chunk)
                
                # --- 🤫 SILENCE PROCESSING ---
                elif is_user_speaking:
                    noise_count = 0
                    silence_count += 1
                    audio_buffer.extend(chunk)
                    
                    if silence_count > SILENCE_LIMIT:
                        logger.info("🤫 User stopped speaking. Processing...")
                        try:
                            await websocket.send_text(json.dumps({"event": "clear", "streamSid": stream_sid}))
                        except Exception:
                            pass
                        
                        if len(audio_buffer) < 4000:
                            logger.warning("⚠️ Audio too short (Background noise). Ignored.")
                        else:
                            # 1. ASYNC STT
                            stt_start = time.time()
                            logger.info("⏳ STT Conversion running in background...")
                            user_text = await asyncio.to_thread(twilio_to_text, bytes(audio_buffer))
                            logger.info(f"⏱️ STT Latency: {time.time() - stt_start:.3f}s")
                            
                            if user_text and len(user_text.strip()) > 3:
                                call_transcript.append(f"User: {user_text}")
                                logger.info(f"👤 User: '{user_text}'")
                                
                                # 2. LOGICAL INTENT FILLER (Zero Latency)
                                filler_intent = detect_intent_for_filler(user_text)
                                if filler_intent and filler_intent in PRE_GENERATED_FILLERS:
                                    try:
                                        await websocket.send_text(json.dumps({
                                            "event": "media", "streamSid": stream_sid,
                                            "media": {"payload": PRE_GENERATED_FILLERS[filler_intent]}
                                        }))
                                        logger.info(f"🧠 Logical Filler Fired: [{filler_intent}]")
                                    except Exception:
                                        pass
                                
                                # 3. LLM STREAMING
                                full_ai_response = ""
                                cancel_current_response = False 
                                ai_speaking_flag = True
                                
                                llm_start = time.time()
                                first_chunk = True
                                
                                for sentence in generate_answer_stream(user_text):
                                    if cancel_current_response:
                                        logger.warning("🛑 LLM Loop halted by Barge-in.")
                                        break 
                                        
                                    if first_chunk:
                                        logger.info(f"⏱️ LLM Time-to-First-Sentence: {time.time() - llm_start:.3f}s")
                                        first_chunk = False
                                        
                                    sentence = sentence.strip()
                                    if not sentence or len(sentence) < 2:
                                        continue
                                    
                                    if "I_DONT_KNOW" in sentence:
                                        from services.knowledge_base import log_unanswered_question
                                        log_unanswered_question(user_text)
                                        sentence = "Right, we currently do not have that information, but we will get back to you soon."

                                    # Human-like conversational polish for voice realism.
                                    sentence = apply_conversational_polish(sentence)
                                    
                                    full_ai_response += sentence + " "
                                    logger.info(f"🤖 AI Chunk: {sentence}")
                                    
                                    # 4. EDGE-TTS GENERATION
                                    tts_start = time.time()
                                    urgency = "high" if any(
                                        token in sentence.lower()
                                        for token in ["important", "urgent", "immediately", "asap"]
                                    ) else "normal"
                                    sentence_audio_base64, tuning_meta = await text_to_twilio_dynamic(
                                        sentence,
                                        urgency=urgency,
                                    )
                                    logger.info(f"⏱️ TTS Edge Generation: {time.time() - tts_start:.3f}s")
                                    logger.info(f"🎚️ Voice Params: {tuning_meta}")
                                    
                                    if cancel_current_response:
                                        break
                                        
                                    try:
                                        await websocket.send_text(json.dumps({
                                            "event": "media", "streamSid": stream_sid,
                                            "media": {"payload": sentence_audio_base64}
                                        }))
                                    except Exception:
                                        cancel_current_response = True
                                        break
                                
                                logger.info(f"⏱️ Total Response Cycle: {time.time() - stt_start:.3f}s")
                                
                                if not cancel_current_response:
                                    call_transcript.append(f"AI: {full_ai_response.strip()}")
                                else:
                                    call_transcript.append(f"AI (Interrupted): {full_ai_response.strip()}...")
                                ai_speaking_flag = False
                                
                            else:
                                logger.warning("⚠️ STT returned empty. Ignored.")
                                
                        audio_buffer = bytearray()
                        is_user_speaking = False
                        silence_count = 0
                        noise_count = 0
                
                else:
                    noise_count = 0
                    audio_buffer.extend(chunk)
                    if len(audio_buffer) > 4000:
                        audio_buffer = audio_buffer[-4000:]
                        
            elif data['event'] == 'stop':
                logger.info("🛑 Call Ended by Twilio.")
                full_convo = "\n".join(call_transcript)
                try:
                    summary = summarize_call(full_convo) if len(call_transcript) > 1 else "No interaction."
                    call_history_db.append({
                        "call_sid": call_sid, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "summary": summary, "transcript": full_convo
                    })
                    save_to_local_file()
                except Exception:
                    pass
                break
                
    except WebSocketDisconnect:
        logger.info("🔌 WebSocket Disconnected Gracefully.")
    except Exception as e:
        logger.error(f"💥 Critical WebSocket Error: {e}", exc_info=True)