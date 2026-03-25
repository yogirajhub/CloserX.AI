# from groq import Groq
# from config import settings
# from services.knowledge_base import read_document, get_admin_answers, log_unanswered_question
# from logger import get_logger

# logger = get_logger(__name__)
# client = Groq(api_key=settings.GROQ_API_KEY)

# def generate_answer(user_query: str) -> str:
#     doc_context = read_document()
#     admin_answers = get_admin_answers()
#     admin_context = "\n".join([f"Q: {k} | A: {v}" for k, v in admin_answers.items()])
    
#     prompt = f"""
#     You are CloserX.AI, a professional voice AI agent.
#     You have TWO sources of knowledge:
#     1. Admin Saved Answers (Highest Priority): {admin_context}
#     2. Official Company Document: {doc_context}

#     STRICT RULES:
#     1. Answer the user's question ONLY using the information from the sources above.
#     2. If the user asks something similar to an "Admin Answer", use that.
#     3. If the answer is completely missing, you MUST reply EXACTLY with: 'I_DONT_KNOW'.
#     4. Keep answers conversational, short, and crisp (1-2 sentences).
#     5. CRITICAL: If the user's sentence feels incomplete or makes no sense, DO NOT say "Question is not completed". Simply say "I'm sorry, I didn't quite catch that. Could you please repeat?"

#     User Question: {user_query}
#     """
    
#     try:
#         response = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama-3.1-8b-instant",
#             temperature=0.1, 
#         )
#         answer = response.choices[0].message.content.strip()
        
#         if "I_DONT_KNOW" in answer:
#             log_unanswered_question(user_query)
#             return "Currently I do not have answers about this question, but we will get back to you soon."
            
#         return answer
#     except Exception as e:
#         logger.error(f"LLM Error: {e}")
#         return "I am having a little trouble connecting right now, could you please repeat that?"
    
# def generate_answer_stream(user_query: str):
#     """LLM jaise-jaise sochega, waise-waise ek-ek sentence (line) yield karega"""
#     doc_context = read_document()
#     admin_answers = get_admin_answers()
#     admin_context = "\n".join([f"Q: {k} | A: {v}" for k, v in admin_answers.items()])
    
#     prompt = f"""
#     You are CloserX.AI, a professional voice AI agent.
#     1. Answer ONLY using the provided contexts.
#     2. If missing, reply EXACTLY with: 'I_DONT_KNOW'.
#     3. EXTREMELY IMPORTANT: Keep answers UNDER 15 WORDS. Be concise.

#     Admin Answers: {admin_context}
#     Document: {doc_context}
#     User: {user_query}
#     """
    
#     try:
#         # MAGIC: stream=True lagane se LLM live type karta hai
#         response = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama-3.1-8b-instant",
#             temperature=0.1, 
#             stream=True 
#         )
        
#         current_sentence = ""
#         for chunk in response:
#             if chunk.choices[0].delta.content:
#                 text = chunk.choices[0].delta.content
#                 current_sentence += text
                
#                 # Jaise hi Full Stop (.), Question Mark (?) ya Exclamation (!) aaye, sentence bhej do
#                 if any(punct in text for punct in ['.', '?', '!']):
#                     yield current_sentence.strip()
#                     current_sentence = ""
                    
#         # Bacha hua aakhiri text
#         if current_sentence.strip():
#             yield current_sentence.strip()
            
#     except Exception as e:
#         logger.error(f"LLM Stream Error: {e}")
#         yield "I am having a little trouble connecting right now."

# def summarize_call(transcript: str) -> str:
#     if not transcript or len(transcript.strip()) < 10:
#         return "Call was too short to summarize."
        
#     prompt = f"""
#     Analyze this transcript of a phone call between an AI agent (CloserX) and a User.
#     Provide a very short, crisp summary (2-3 sentences max) of the outcome. No bullet points.
#     Transcript:
#     {transcript}
#     """
#     try:
#         response = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama-3.1-8b-instant",
#             temperature=0.3,
#         )
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         logger.error(f"Summary Error: {e}")
#         return "Could not generate summary."



from groq import Groq
from config import settings
from services.knowledge_base import read_document, get_admin_answers, log_unanswered_question
from logger import get_logger
import random
import re

logger = get_logger(__name__)
client = Groq(api_key=settings.GROQ_API_KEY)

INDIAN_BACKCHANNELS = ["right", "okay", "hmm", "got it", "let me check"]

def detect_intent_for_filler(user_text: str) -> str:
    """User ke sawal ka intent samajhta hai taaki perfect filler fire ho"""
    if not user_text:
        return None
        
    text_lower = user_text.lower()
    words = text_lower.split()

    if len(words) <= 3:
        return None 

    problem_keywords = ["problem", "issue", "not working", "bad", "broken", "complain", "damage"]
    if any(word in text_lower for word in problem_keywords):
        return "empathetic" 

    question_keywords = ["what", "how", "why", "when", "where", "can you", "do you"]
    if any(text_lower.startswith(q) for q in question_keywords):
        return "thinking" 

    return "affirmative"

def generate_answer_stream(user_query: str):
    doc_context = read_document()
    admin_answers = get_admin_answers()
    admin_context = "\n".join([f"Q: {k} | A: {v}" for k, v in admin_answers.items()])
    
    # 🔥 ULTIMATE DEBUGGER: Terminal me dikhayega ki AI ne kitne words ki file padhi!
    logger.info(f"📄 Knowledge Base Check: Loaded {len(doc_context)} characters from document.")
    
    # System Role me strict rules daale hain, ab ye 100% follow karega
    system_prompt = f"""You are CloserX, a highly professional customer support agent.
You must STRICTLY follow these rules:
1. You are provided with a 'Knowledge Base' below. You MUST ONLY answer questions using the information present in this Knowledge Base.
2. If the user asks a question and the answer is NOT explicitly written in the Knowledge Base, you MUST reply EXACTLY with the word: I_DONT_KNOW. 
3. Do not make up facts, do not hallucinate, and do not use outside knowledge.
4. Keep answers conversational and short (under 18 words).
5. Tone: neutral Indian English, warm, semi-formal, professional.
6. Use light conversational style naturally (for example: "right", "okay", "I understand", "just to confirm").
7. Avoid overly Western slang and avoid robotic phrasing.
8. If clarifying the query, use "So you're looking for..." or "Just to confirm...".
9. Slightly imperfect spoken style is allowed, but keep it polite and clear.

--- KNOWLEDGE BASE START ---
{admin_context}

{doc_context}
--- KNOWLEDGE BASE END ---
"""
    
    try:
        response = client.chat.completions.create(
            # NAYA CHANGE: System aur User roles ko alag-alag kar diya
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ],
            model="llama-3.1-8b-instant",
            temperature=0.0, # Temperature 0.0 matab 0% creativity, 100% factual
            stream=True 
        )
        
        current_sentence = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                text = chunk.choices[0].delta.content
                current_sentence += text
                
                if any(punct in text for punct in ['.', '?', '!', ',']):
                    if len(current_sentence.strip()) > 2: 
                        yield current_sentence.strip()
                        current_sentence = ""
                    
        if current_sentence.strip():
            yield current_sentence.strip()
            
    except Exception as e:
        logger.error(f"LLM Stream Error: {e}")
        yield "I am having a little trouble connecting right now."


def apply_conversational_polish(text: str) -> str:
    """
    Adds light spoken-style polish with tiny randomness.
    Keeps utterances short for low latency TTS chunks.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return "Okay, could you please repeat that?"

    if cleaned.lower().startswith("i dont know") or "I_DONT_KNOW" in cleaned:
        return cleaned

    # Soften hard starts and create natural Indian conversational entry.
    if random.random() < 0.35:
        prefix = random.choice(INDIAN_BACKCHANNELS)
        if not cleaned.lower().startswith(tuple(INDIAN_BACKCHANNELS)):
            cleaned = f"{prefix}, {cleaned}"

    # Convert rigid statements to conversational confirmations.
    cleaned = re.sub(r"^You can ", "Sure, you can ", cleaned)
    cleaned = re.sub(r"^Please ", "Just a moment please, ", cleaned)

    # Keep chunk compact.
    words = cleaned.split()
    if len(words) > 22:
        cleaned = " ".join(words[:22]).rstrip(",.") + "."

    return cleaned

def summarize_call(transcript: str) -> str:
    if not transcript or len(transcript.strip()) < 10:
        return "Call was too short to summarize."
        
    prompt = f"""
    Analyze this transcript of a phone call. Provide a very short, crisp summary (1-2 sentences max).
    Transcript: {transcript}
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Summary Error: {e}")
        return "Could not generate summary."