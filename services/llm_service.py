# from groq import Groq
# from config import settings
# from services.knowledge_base import get_knowledge_context, log_unanswered_question
# from logger import get_logger

# logger = get_logger(__name__)
# client = Groq(api_key=settings.GROQ_API_KEY)

# def generate_answer(user_query: str) -> str:
#     context = get_knowledge_context()
    
#     # NAYA STRICT PROMPT: Voice call ke hisaab se optimized
#     prompt = f"""
#     You are CloserX.AI, a highly professional and energetic AI sales agent talking to a user over a phone call. 
    
#     STRICT RULES FOR YOUR RESPONSE:
#     1. KEEP IT SHORT & CRISP: Your answer MUST be extremely concise, ideally 1 or 2 short sentences.
#     2. BE CONVERSATIONAL: Speak like a real human on a phone call. Do not use bullet points, special formatting, or long lists.
#     3. NO YAPPING: Get straight to the point.
    
#     Using ONLY the following context, answer the user's question.
#     If the answer is not in the context, reply EXACTLY with this phrase: 'Currently I do not have answers about this question, but we will get back to you soon.'
    
#     Context:
#     {context}
    
#     User Question: {user_query}
#     """
    
#     try:
#         response = client.chat.completions.create(
#             messages=[{"role": "user", "content": prompt}],
#             model="llama-3.1-8b-instant",
#             temperature=0.3, # Temperature thodi kam ki hai taaki answer strict aur focused rahe
#         )
        
#         answer = response.choices[0].message.content
        
#         # Unanswered track karne ka logic
#         if "Currently I do not have answers" in answer:
#             log_unanswered_question(user_query)
            
#         return answer
#     except Exception as e:
#         logger.error(f"LLM Error: {e}")
#         return "I am having a little trouble connecting right now, could you please repeat that?"

# def summarize_call(transcript: str) -> str:
#     prompt = f"Summarize this sales call concisely without losing context:\n\n{transcript}"
#     response = client.chat.completions.create(
#         messages=[{"role": "user", "content": prompt}],
#         model="llama-3.1-8b-instant",
#     )
#     return response.choices[0].message.content

# # services/llm_service.py ke aakhir me add karein

# def generate_call_summary(transcript: str) -> str:
#     """Call khatam hone par transcript ki short summary banata hai"""
#     if not transcript or len(transcript.strip()) < 10:
#         return "Call was too short to summarize."
        
#     prompt = f"""
#     Analyze the following transcript of a phone call between an AI sales agent (CloserX) and a User.
#     Provide a very short, crisp summary (2-3 sentences max) of the context and the final outcome or action item.
#     Do not use bullet points. Write in a clear, professional paragraph.
    
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
#         return "Could not generate summary due to an error."


from groq import Groq
from config import settings
from services.knowledge_base import read_document, get_admin_answers, log_unanswered_question
from logger import get_logger

logger = get_logger(__name__)
client = Groq(api_key=settings.GROQ_API_KEY)

def generate_answer(user_query: str) -> str:
    doc_context = read_document()
    admin_answers = get_admin_answers()
    admin_context = "\n".join([f"Q: {k} | A: {v}" for k, v in admin_answers.items()])
    
    prompt = f"""
    You are CloserX.AI, a professional voice AI agent.
    You have TWO sources of knowledge:
    1. Admin Saved Answers (Highest Priority): {admin_context}
    2. Official Company Document: {doc_context}

    STRICT RULES:
    1. Answer the user's question ONLY using the information from the sources above.
    2. If the user asks something similar to an "Admin Answer", use that.
    3. If the answer is completely missing from BOTH sources, you MUST reply EXACTLY with: 'I_DONT_KNOW'.
    4. Keep answers conversational, short, and crisp (1-2 sentences). No bullet points.

    User Question: {user_query}
    """
    
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.1, 
        )
        answer = response.choices[0].message.content.strip()
        
        if "I_DONT_KNOW" in answer:
            log_unanswered_question(user_query)
            return "Currently I do not have answers about this question, but we will get back to you soon."
            
        return answer
    except Exception as e:
        logger.error(f"LLM Error: {e}")
        return "I am having a little trouble connecting right now, could you please repeat that?"

def summarize_call(transcript: str) -> str:
    if not transcript or len(transcript.strip()) < 10:
        return "Call was too short to summarize."
        
    prompt = f"""
    Analyze this transcript of a phone call between an AI agent (CloserX) and a User.
    Provide a very short, crisp summary (2-3 sentences max) of the outcome. No bullet points.
    Transcript:
    {transcript}
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