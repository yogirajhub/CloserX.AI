# import json
# import os
# from typing import List, Dict

# KNOWLEDGE_FILE = "data/knowledge.json"
# UNANSWERED_FILE = "data/unanswered.json"

# def load_json(filepath: str) -> List[Dict]:
#     if not os.path.exists(filepath):
#         return []
        
#     # Check if the file is completely empty before trying to load it
#     if os.path.getsize(filepath) == 0:
#         return []
        
#     with open(filepath, 'r') as f:
#         try:
#             return json.load(f)
#         except json.JSONDecodeError:
#             return [] # If the JSON is broken, return an empty list

# def save_json(filepath: str, data: List[Dict]):
#     with open(filepath, 'w') as f:
#         json.dump(data, f, indent=4)

# def get_knowledge_context() -> str:
#     data = load_json(KNOWLEDGE_FILE)
#     return "\n".join([f"Q: {item['q']} A: {item['a']}" for item in data])

# def log_unanswered_question(question: str):
#     unanswered = load_json(UNANSWERED_FILE)
#     unanswered.append({"id": len(unanswered) + 1, "question": question})
#     save_json(UNANSWERED_FILE, unanswered)

# def answer_question(question_id: int, answer: str):
#     unanswered = load_json(UNANSWERED_FILE)
#     question_text = ""
    
#     # Remove from unanswered
#     remaining = []
#     for q in unanswered:
#         if q["id"] == question_id:
#             question_text = q["question"]
#         else:
#             remaining.append(q)
#     save_json(UNANSWERED_FILE, remaining)

#     # Add to knowledge base
#     if question_text:
#         knowledge = load_json(KNOWLEDGE_FILE)
#         knowledge.append({"q": question_text, "a": answer})
#         save_json(KNOWLEDGE_FILE, knowledge)


import json
import os
from typing import List, Dict

DOC_FILE = "data/document_context.txt"
ADMIN_ANSWERS_FILE = "data/admin_answers.json"
UNANSWERED_FILE = "data/unanswered.json"

# Make sure data folder exists
os.makedirs("data", exist_ok=True)

def load_json(filepath: str, default_type):
    if not os.path.exists(filepath) or os.path.getsize(filepath) == 0:
        return default_type
    with open(filepath, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default_type

def save_json(filepath: str, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# --- DOCUMENT RAG LOGIC ---
def read_document() -> str:
    if os.path.exists(DOC_FILE):
        with open(DOC_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return "No document uploaded yet."

def update_document(text: str):
    with open(DOC_FILE, "w", encoding="utf-8") as f:
        f.write(text)

# --- ADMIN & UNANSWERED LOGIC ---
def get_admin_answers() -> dict:
    return load_json(ADMIN_ANSWERS_FILE, {})

def get_unanswered_questions() -> list:
    return load_json(UNANSWERED_FILE, [])

def log_unanswered_question(question: str):
    unanswered = get_unanswered_questions()
    # Duplicate check
    if not any(q.get("question", "").lower() == question.lower() for q in unanswered):
        new_id = len(unanswered) + 1 if not unanswered else max(q["id"] for q in unanswered) + 1
        unanswered.append({"id": new_id, "question": question})
        save_json(UNANSWERED_FILE, unanswered)

def answer_question(question_id: int, answer: str):
    unanswered = get_unanswered_questions()
    question_text = ""
    
    remaining = []
    for q in unanswered:
        if q["id"] == question_id:
            question_text = q["question"]
        else:
            remaining.append(q)
    save_json(UNANSWERED_FILE, remaining)

    if question_text:
        admin_answers = get_admin_answers()
        admin_answers[question_text.lower()] = answer
        save_json(ADMIN_ANSWERS_FILE, admin_answers)