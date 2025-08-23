<div align="center">

# 🤖 AI Chat Assistant

Multi‑persona, real‑time AI chat app powered by **Google Gemini (gemini‑1.5‑flash)**, built with **Flask** + **Vanilla JS**. Clean UI, fast streaming answers, local persistence, role switching, dark mode – production‑ready and résumé‑showcase friendly.

![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white&style=flat-square) ![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask&style=flat-square) ![Gemini](https://img.shields.io/badge/Model-gemini--1.5--flash-orange?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

<img src="docs/preview-light.png" alt="Light Mode Screenshot" width="640"/><br/>
<sub><em>Dark & Light themes • Streaming responses • Role selector</em></sub>

</div>

---

## 💼 Résumé Pitch (copy/paste)
Designed and implemented a production‑ready multi‑persona AI chat platform using Flask + Google Gemini (1.5‑flash) with live streaming (SSE), local persistence, semantic role prompts, theming, and extensible architecture. Added intent overrides (model + authors), performance‑aware history trimming, and structured logging.

## ✨ Feature Highlights
| Category | Capabilities |
|----------|--------------|
| Core Chat | Real‑time SSE streaming, markdown formatting, code blocks |
| AI Personalities | Helpful Assistant, Teacher, Financial Advisor, Creative Writer, Technical Expert (easily extendable) |
| UX | Typing indicator, auto‑grow input, role switching, dark/light theme, animated credits footer |
| Persistence | Session + localStorage hybrid (safe vs cookie size limits) |
| Reliability | Graceful error handling, health endpoint, debug & test routes, history trimming |
| Custom Intents | Built‑in answers for “Which model...?” / “Who developed you?” |

## 🧠 Architecture Overview
```
Browser
   ├── chat.js (UI logic, streaming parser, localStorage cache)
   └── style.css (theme tokens + responsive layout)
Flask App (app.py)
   ├── /chat (JSON)            ← fallback
   ├── /chat/stream (SSE)      ← primary real-time path
   ├── /get_history /clear_chat
   ├── /health /debug_session
   └── Role prompt builder → Gemini (gemini-1.5-flash)
```

## 🚀 Quick Start
```bash
git clone <your-repo-url>
cd ai-chat-assistant
pip install -r requirements.txt
python app.py  # visit http://localhost:5000
```
Set your API key in `config.py` (or export `GEMINI_API_KEY`).

## 🔧 Configuration Cheat Sheet
| Setting | File | Purpose |
|---------|------|---------|
| GEMINI_API_KEY | `config.py` | Model auth |
| AI_ROLES | `config.py` | Persona system prompts |
| MAX_CHAT_HISTORY | `config.py` | Memory window limit |
| Streaming Endpoint | `/chat/stream` | SSE token flow |

## 🛠 Tech Stack
| Layer | Tools |
|-------|-------|
| Backend | Flask, google-generativeai |
| Frontend | Vanilla JS, Fetch API, SSE |
| Styling | CSS custom properties, responsive layout |
| AI Model | Google Gemini 1.5 Flash |

## 🏎 Performance & Design Notes
* Streaming via SSE avoids blocking and enables token‑level UX.
* LocalStorage prevents cookie bloat (browser session size limits) while still restoring state after refresh.
* History trimming ensures prompt size stays within efficient limits.
* Intent short‑circuits for common meta questions reduce API calls.

## 🧪 Optional Test Prompts
| Purpose | Prompt |
|---------|--------|
| Model check | Which model are you using? |
| Credits | Who developed you? |
| Persona switch | Act as a teacher and explain gravity. |
| Streaming | Give me 5 creative startup ideas, elaborate each. |

## � Project Layout
```
app.py              # Main Flask app (stream + JSON endpoints)
backend/app.py      # Alt/legacy API module (retained)
static/js/chat.js   # Frontend client logic
static/css/style.css# Theming & layout
templates/index.html# Main UI
config.py           # Settings & roles
```

## 🌐 Deployment Snippets
Gunicorn (Linux):
```bash
gunicorn -w 4 -k gthread -b 0.0.0.0:5000 app:app
```
Render / Railway: add `GEMINI_API_KEY` & (optionally) `SECRET_KEY` environment vars.

## 🔐 Security Checklist
☑ Never commit real keys
☑ Rotate API keys periodically
☑ Use HTTPS in production
☑ Add rate limiting / auth before multi‑tenant release

## 🗺 Roadmap Ideas
- Vector memory / embeddings
- User auth + saved conversations
- File & image attachments
- Export (PDF / Markdown)
- Plugin / tool calling system

## 🐛 Troubleshooting Quick Hits
| Issue | Fix |
|-------|-----|
| No response appears | Check browser console; confirm `/chat/stream` 200 |
| Empty model reply | Verify API quota / key |
| Styling off | Hard refresh / clear cache |
| Session lost | localStorage cleared or new browser context |

## 🤝 Contributing
1. Fork
2. Create feature branch
3. Commit with conventional style
4. PR with concise description & screenshot

## � Credits
Original concept & initial implementation: **Ritesh**  
Stabilization, fixes & streaming enhancements: **Himanshu**  
Built with ❤️ using Flask & Google Gemini AI.

## � License
MIT – free to use & adapt. Retain credits if you showcase.

## 📬 Contact / Portfolio Hooks
Add your personal links here (GitHub • LinkedIn • Portfolio) when publishing.

---
> Tip: For your résumé, link directly to this repo and mention “Implemented streaming AI chat (Gemini 1.5 Flash) with multi‑persona prompts, SSE, and persistence.”
