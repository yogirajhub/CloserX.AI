<div align="center">

<br/>

```
   ██████╗██╗      ██████╗ ███████╗███████╗██████╗ ██╗  ██╗
  ██╔════╝██║     ██╔═══██╗██╔════╝██╔════╝██╔══██╗╚██╗██╔╝
  ██║     ██║     ██║   ██║███████╗█████╗  ██████╔╝ ╚███╔╝ 
  ██║     ██║     ██║   ██║╚════██║██╔══╝  ██╔══██╗ ██╔██╗ 
  ╚██████╗███████╗╚██████╔╝███████║███████╗██║  ██║██╔╝ ██╗
   ╚═════╝╚══════╝ ╚═════╝ ╚══════╝╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝
```

### AI-Powered Outbound Sales Calling Agent

*Real-time voice conversations · RAG knowledge base · Self-learning feedback loop*

> **CloserX** is a production-ready AI sales agent that handles outbound calls autonomously —  
> answering questions from your knowledge base, logging unknowns, and getting smarter over time.

<br/>

</div>

---

## 📌 Table of Contents

- [✨ Features](#-features)
- [🏗️ System Architecture](#️-system-architecture)
- [🚀 Getting Started](#-getting-started)
- [📁 Project Structure](#-project-structure)
- [🌐 Dashboard Overview](#-dashboard-overview)
- [🛣️ Roadmap](#️-roadmap)
- [👨‍💻 Author](#-author)

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 📞 Real-Time Voice Interaction
Two-way live audio using **Twilio WebSocket Media Streams** — minimal latency, seamless conversation flow.

### 🧠 RAG-Based Knowledge System
Upload **PDFs & TXT files** (FAQs, policies, brochures). AI responds strictly from your content — fully controlled intelligence.

### 🛑 Smart Barge-In (Interruption Handling)
Detects mid-speech user input, **instantly stops TTS**, and switches to listening mode — just like a real agent.

### 🔄 Self-Learning Feedback Loop
Unknown queries are **auto-logged**. Admin adds answers → AI permanently learns and improves.

</td>
<td width="50%">

### 🗑️ Admin Memory Control
Accept or reject irrelevant queries to maintain a **clean, meaningful knowledge base** over time.

### 📝 Call Logging & Summarization
Full transcription + **AI-generated summaries** via Groq LLM, stored locally for instant access.

### ⚡ Ultra-Fast LLM Responses
Powered by **Groq (LLaMA 3.1 8B Instant)** — near real-time replies that feel natural.

### 🎛️ Web Dashboard
Manage everything from one place: initiate calls, upload docs, handle queries, review logs.

</td>
</tr>
</table>

---

## 🏗️ System Architecture

```
                         ┌─────────────────────────────────────────────┐
                         │              📱  USER CALL                  │
                         └─────────────────────┬───────────────────────┘
                                               │
                         ┌─────────────────────▼───────────────────────┐
                         │         📡  TWILIO MEDIA STREAMS            │
                         │         WebSocket Telephony Layer           │
                         └─────────────────────┬───────────────────────┘
                                               │
                         ┌─────────────────────▼───────────────────────┐
                         │       ⚡  FASTAPI WEBSOCKET SERVER           │
                         │       Real-time request orchestration       │
                         └────────┬──────────────────────┬─────────────┘
                                  │                      │
               ┌──────────────────▼──────┐   ┌──────────▼──────────────┐
               │   🎙️  AUDIO LAYER       │   │  🧠  INTELLIGENCE LAYER  │
               │   STT ↔ TTS Processing  │   │  Groq LLM (RAG + Prompt) │
               └─────────────────────────┘   └──────────┬──────────────┘
                                                        │
                         ┌──────────────────────────────▼───────────────┐
                         │           💾  LOCAL JSON STORAGE              │
                         │   call_history · unanswered · knowledge base  │
                         └───────────────────────────────────────────────┘
```

### Layer Breakdown

| Layer | Technology | Responsibility |
|---|---|---|
| **Telephony** | Twilio | Handles calls & WebSocket connection |
| **Audio** | Python STT/TTS | Converts audio ↔ text in real-time |
| **Intelligence** | Groq (LLaMA 3.1) | Processes queries via RAG + prompting |
| **Storage** | Local JSON (`/data`) | Call history, unanswered queries, KB |

---

## 🚀 Getting Started

### Prerequisites

Before you begin, make sure you have the following:

- **Python 3.11+** installed
- Active accounts on:
  - 🟥 [Twilio](https://www.twilio.com/) — for telephony & WebSockets
  - 🟧 [Groq](https://console.groq.com/) — for LLM inference
  - 🟦 [Ngrok](https://ngrok.com/) — for local tunnel exposure

---

### Step 1 — Clone the Repository

```bash
git clone https://github.com/yourusername/closerx-ai.git
cd closerx-ai
```

### Step 2 — Create a Virtual Environment

```bash
python -m venv venv
```

**Activate it:**

```bash
# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### Step 3 — Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables

Create a `.env` file in the root directory:

```env
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
GROQ_API_KEY=your_groq_api_key
```

> ⚠️ **Never commit `.env` to version control.** It's already included in `.gitignore`.

### Step 5 — Run the Application

Open **two separate terminals**:

```bash
# Terminal 1 — Start FastAPI Server
uvicorn main:app --reload
```

```bash
# Terminal 2 — Expose via Ngrok
ngrok http 8000
```

### Step 6 — Access the Dashboard

| Environment | URL |
|---|---|
| Local | `http://localhost:8000` |
| Local (alt) | `http://127.0.0.1:8000` |
| Public | Your Ngrok-generated HTTPS URL |

---

## 📁 Project Structure

```
CloserX_AI/
│
├── 📄 main.py                  # FastAPI server & WebSocket logic
├── ⚙️  config.py               # Environment config loader
├── 📋 logger.py                # Logging setup
│
├── 🛠️  services/
│   ├── audio_service.py        # STT & TTS pipeline
│   ├── llm_service.py          # Groq LLM + call summarization
│   └── knowledge_base.py       # JSON DB + document handling
│
├── 💾 data/                    # Auto-generated local storage
│   ├── call_history.json       # Full call transcripts & summaries
│   ├── unanswered.json         # Queries the AI couldn't answer
│   ├── admin_answers.json      # Admin-provided knowledge updates
│   └── document_context.txt   # Extracted text from uploaded docs
│
├── 🎨 static/
│   ├── css/style.css           # Dashboard styling
│   └── js/main.js              # Frontend interaction logic
│
├── 🖼️  templates/
│   └── index.html              # Web dashboard UI
│
└── 🔒 .env                     # API keys (git-ignored)
```

---

## 🌐 Dashboard Overview

The built-in web dashboard lets you manage everything without touching the code:

| Section | What You Can Do |
|---|---|
| 📞 **Outbound Calls** | Initiate AI-powered calls to any number |
| 📚 **Knowledge Base** | Upload PDFs & TXT files as the AI's context |
| ❓ **Unanswered Queries** | Review, answer, or reject unknown questions |
| 📜 **Call Logs** | Browse full transcripts and AI-generated summaries |

---

## 🛣️ Roadmap

| Status | Feature |
|---|---|
| 🔲 | **Streaming STT/TTS** — Replace gTTS with Deepgram/Cartesia for ultra-low latency |
| 🔲 | **Voice Activity Detection (VAD)** — Silero VAD for instant silence detection |
| 🔲 | **Inbound Calling Support** — Let users call the AI agent directly |
| 🔲 | **Database Upgrade** — Migrate from JSON → PostgreSQL / Vector DB |
| 🔲 | **Advanced RAG** — Add embeddings + semantic search for smarter retrieval |

---

## 👨‍💻 Author

<div align="center">

<br/>

**Yogiraj Gautam**

*Built with ❤️ for AI sales automation and real-time conversational systems.*

<br/>

[![GitHub](![alt text](Product.png))](https://github.com/yogirajhub)

<br/>

---

*⭐ If you found this project useful, please consider giving it a star!*

</div>
