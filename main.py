# import base64
# from fastapi import FastAPI, WebSocket, Request, BackgroundTasks
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.templating import Jinja2Templates
# from pydantic import BaseModel
# import json
# import os
# from datetime import datetime

# from services.llm_service import generate_answer, summarize_call
# from services.knowledge_base import load_json, answer_question
# from config import settings
# from logger import get_logger
# from twilio.rest import Client
# from fastapi import WebSocketDisconnect
# from services.audio_service import twilio_to_text, text_to_twilio
# import asyncio
# from datetime import datetime
# from services.llm_service import generate_call_summary # Naya function import kiya

# # Calls ka data store karne ke liye (Server restart hone par ye clear ho jayega)
# # main.py mein apne purane call_history_db = [] ko isse replace kar dein:

# # Naya Local Storage Logic
# DB_FILE = "call_history.json"

# # Jab server start hoga, toh pehle check karega ki kya purani file exist karti hai
# if os.path.exists(DB_FILE):
#     with open(DB_FILE, "r") as f:
#         call_history_db = json.load(f)
# else:
#     call_history_db = []

# def save_to_local_file():
#     """Ye function list ko json file me permanently save karega"""
#     with open(DB_FILE, "w") as f:
#         json.dump(call_history_db, f, indent=4)

# # Is class ko define karna zaroori hai error hatane ke liye
# class CallRequest(BaseModel):
#     phone_number: str
# logger = get_logger("main")

# app = FastAPI()
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")

# class AnswerPayload(BaseModel):
#     id: int
#     answer: str

# @app.get("/", response_class=HTMLResponse)
# async def index(request: Request):
#     return templates.TemplateResponse("index.html", {"request": request})

# @app.get("/api/unanswered")
# async def get_unanswered():
#     return load_json("data/unanswered.json")

# @app.get("/api/call_history")
# async def get_call_history():
#     """Dashboard ko call history bhejne ke liye"""
#     # [::-1] ka matlab hai list ko reverse karna, taaki sabse nayi call sabse upar dikhe
#     return {"history": call_history_db[::-1]}

# @app.post("/api/answer")
# async def submit_answer(payload: AnswerPayload):
#     answer_question(payload.id, payload.answer)
#     return {"status": "success"}

# # --- TWILIO CALLING LOGIC ---
# @app.post("/twiml")
# async def twilio_webhook(request: Request):
#     """Initial Twilio Webhook to start the WebSocket stream"""
#     host = settings.NGROK_URL.replace("https://", "")
#     xml = f"""<?xml version="1.0" encoding="UTF-8"?>
#     <Response>
#         <Connect>
#             <Stream url="wss://{host}/media-stream" />
#         </Connect>
#     </Response>"""
#     return HTMLResponse(content=xml, media_type="application/xml")

# @app.websocket("/media-stream")
# async def websocket_endpoint(websocket: WebSocket):
#     await websocket.accept()
#     stream_sid = None
#     call_sid = None  # NAYA CHANGE: Call SID ko track karne ke liye variable add kiya
    
#     # NAYA BADA CHANGE: Ab hum text nahi, raw audio bytes store karenge
#     audio_buffer = bytearray()
#     call_transcript = []
    
#     try:
#         while True:
#             message = await websocket.receive_text()
#             data = json.loads(message)
            
#             if data['event'] == 'connected':
#                 logger.info("Twilio WebSocket Connected Successfully!")

#             # ... (baaki code)
#             elif data['event'] == 'start':
#                 stream_sid = data['start']['streamSid']
#                 # NAYI LINE: Twilio ka asli Call SID capture karein
#                 call_sid = data['start'].get('callSid', 'Unknown_Call_SID') 
                
#                 logger.info(f"Incoming Stream Started: {stream_sid} | Call SID: {call_sid}")
#                 # ... (baaki greeting wala code)
                
#                 greeting_text = "Hello, this is CloserX. How can I help you today?"
#                 call_transcript.append(f"AI: {greeting_text}")
                
#                 try:
#                     base64_audio = text_to_twilio(greeting_text)
#                     await websocket.send_text(json.dumps({
#                         "event": "media",
#                         "streamSid": stream_sid,
#                         "media": {"payload": base64_audio}
#                     }))
#                     logger.info("Greeting voice sent to user.")
#                 except Exception as e:
#                     logger.error(f"Error converting/sending greeting: {e}")
                
#             elif data['event'] == 'media':
#                 # NAYA CHANGE: Pehle Base64 decode karein, phir buffer mein dalein
#                 chunk_bytes = base64.b64decode(data['media']['payload'])
#                 audio_buffer.extend(chunk_bytes)
                
#                 # Twilio 1 second mein 8000 bytes bhejta hai. 32000 = 4 Seconds ki aawaz.
#                 if len(audio_buffer) > 32000: 
#                     logger.info("Analyzing user audio chunk...")
                    
#                     # Bytearray ko normal bytes mein convert karke bhejein
#                     user_text = twilio_to_text(bytes(audio_buffer))
                    
#                     # Sliding Window: Aakhiri 1 second (8000 bytes) bachayein taaki word na kate
#                     audio_buffer = audio_buffer[-8000:] 
                    
#                     if user_text and user_text.strip():
#                         logger.info(f"User said: {user_text}")
#                         call_transcript.append(f"User: {user_text}")
                        
#                         # Aawaz pakadte hi buffer khali karein
#                         audio_buffer = bytearray()
                        
#                         ai_answer = generate_answer(user_text)
#                         logger.info(f"AI Answer: {ai_answer}")
#                         call_transcript.append(f"AI: {ai_answer}")
                        
#                         try:
#                             ai_audio_base64 = text_to_twilio(ai_answer)
#                             await websocket.send_text(json.dumps({
#                                 "event": "media",
#                                 "streamSid": stream_sid,
#                                 "media": {"payload": ai_audio_base64}
#                             }))
#                             logger.info("AI voice sent back to user.")
#                         except Exception as e:
#                             logger.error(f"Error sending AI audio: {e}")
                        
#             elif data['event'] == 'stop':
#                 logger.info("Call disconnected.")
#                 full_conversation = "\n".join(call_transcript)
                
#                 summary = "User did not speak."
#                 if len(call_transcript) > 1:
#                     logger.info("Generating call summary...")
#                     summary = generate_call_summary(full_conversation)
                
#                 # NAYA: Call SID ke sath data record karein
#                 call_record = {
#                     "call_sid": call_sid,  # Twilio ki unique ID
#                     "stream_sid": stream_sid,
#                     "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                     "phone": "Inbound/Outbound Call",
#                     "summary": summary,
#                     "transcript": full_conversation
#                 }
                
#                 # List me add karein aur turant File me Save kar dein
#                 call_history_db.append(call_record)
#                 save_to_local_file() # 🔥 Ye line file banayegi/update karegi
                
#                 logger.info(f"Call permanently saved to {DB_FILE}")
#                 break
                
#     except WebSocketDisconnect:
#         logger.info("WebSocket disconnected gracefully.")
#     except Exception as e:
#         logger.error(f"Error in WebSocket: {e}")
        
# @app.post("/api/make_call")
# async def make_outbound_call(payload: CallRequest):
#     """Dashboard se outbound call initiate karne ke liye"""
#     try:
#         client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        
#         # Twilio ko batana hai ki call uthne ke baad kya karna hai
#         # Hum usko apne /twiml endpoint par bhejenge jo WebSocket connect karega
#         twiml_url = f"{settings.NGROK_URL}/twiml"
        
#         call = client.calls.create(
#             to=payload.phone_number,
#             from_=settings.TWILIO_PHONE_NUMBER,
#             url=twiml_url
#         )
#         logger.info(f"Call initiated successfully. SID: {call.sid}")
#         return {"status": "success", "message": f"Calling {payload.phone_number}..."}
        
#     except Exception as e:
#         logger.error(f"Failed to make call: {e}")
#         return {"status": "error", "message": str(e)}

import base64
import json
import os
import io
import PyPDF2  # NAYI LIBRARY: PDF read karne ke liye
from datetime import datetime
from fastapi import FastAPI, WebSocket, Request, UploadFile, File, WebSocketDisconnect
from fastapi.responses import HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from twilio.rest import Client

from services.llm_service import generate_answer, summarize_call
from services.knowledge_base import get_unanswered_questions, answer_question, update_document
from services.audio_service import twilio_to_text, text_to_twilio
from config import settings
from logger import get_logger

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
    with open(DB_FILE, "w") as f: 
        json.dump(call_history_db, f, indent=4)

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
    """Upload TXT or PDF document for RAG AI"""
    try:
        content = await file.read()
        text = ""
        
        # Agar file PDF hai, toh extract text
        if file.filename.lower().endswith(".pdf"):
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        else:
            # Agar normal txt file hai
            text = content.decode("utf-8")
            
        update_document(text)
        return {"message": f"{file.filename} learned successfully!"}
        
    except Exception as e:
        logger.error(f"Upload Error: {e}")
        return {"status": "error", "message": "Failed to read the file. Please check format."}

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

@app.post("/api/make_call")
async def make_outbound_call(payload: CallRequest):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        twiml_url = f"{settings.NGROK_URL}/twiml"
        call = client.calls.create(to=payload.phone_number, from_=settings.TWILIO_PHONE_NUMBER, url=twiml_url)
        return {"status": "success", "message": f"Calling {payload.phone_number}...", "call_sid": call.sid}
    except Exception as e:
        logger.error(f"Failed to make call: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/twiml")
async def twilio_webhook():
    host = settings.NGROK_URL.replace("https://", "").replace("http://", "")
    xml = f"""<?xml version="1.0" encoding="UTF-8"?><Response><Connect><Stream url="wss://{host}/media-stream" /></Connect></Response>"""
    return Response(content=xml, media_type="text/xml")

# --- WEBSOCKET ---
@app.websocket("/media-stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    stream_sid = None
    call_sid = None 
    audio_buffer = bytearray()
    call_transcript = []
    
    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            
            if data['event'] == 'start':
                stream_sid = data['start']['streamSid']
                call_sid = data['start'].get('callSid', 'Unknown_Call_SID') 
                logger.info(f"Stream Started: {stream_sid} | Call SID: {call_sid}")
                
                greeting_text = "Hello, this is CloserX. How can I help you today?"
                call_transcript.append(f"AI: {greeting_text}")
                
                try:
                    await websocket.send_text(json.dumps({
                        "event": "media", "streamSid": stream_sid,
                        "media": {"payload": text_to_twilio(greeting_text)}
                    }))
                except Exception as e:
                    logger.error(f"Error greeting: {e}")
                
            elif data['event'] == 'media':
                audio_buffer.extend(base64.b64decode(data['media']['payload']))
                
                if len(audio_buffer) > 32000: # 4 Seconds window
                    user_text = twilio_to_text(bytes(audio_buffer))
                    audio_buffer = audio_buffer[-8000:] # Sliding window 1s overlap
                    
                    if user_text and user_text.strip():
                        call_transcript.append(f"User: {user_text}")
                        logger.info(f"User: {user_text}")
                        
                        # Barge-in (Stop AI from speaking old text)
                        await websocket.send_text(json.dumps({"event": "clear", "streamSid": stream_sid}))
                        
                        audio_buffer = bytearray()
                        ai_answer = generate_answer(user_text)
                        call_transcript.append(f"AI: {ai_answer}")
                        
                        try:
                            await websocket.send_text(json.dumps({
                                "event": "media", "streamSid": stream_sid,
                                "media": {"payload": text_to_twilio(ai_answer)}
                            }))
                        except Exception as e:
                            logger.error(f"Error sending audio: {e}")
                        
            elif data['event'] == 'stop':
                full_convo = "\n".join(call_transcript)
                summary = "User did not speak."
                if len(call_transcript) > 1:
                    summary = summarize_call(full_convo)
                
                call_history_db.append({
                    "call_sid": call_sid, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "summary": summary, "transcript": full_convo
                })
                save_to_local_file()
                break
                
    except WebSocketDisconnect:
        logger.info("WebSocket disconnected gracefully.")