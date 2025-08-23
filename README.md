<div align="center">

# 🤖 AI Chat Assistant

An elegant, fast, multi‑persona AI chat experience powered by **Google Gemini (gemini‑1.5‑flash)**. Built with **Flask + Vanilla JavaScript**. Streaming responses, smart role prompts, dark/light theming, and a clean developer‑friendly architecture.

![Status](https://img.shields.io/badge/Status-Active-success?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white&style=flat-square) ![Flask](https://img.shields.io/badge/Flask-Backend-black?logo=flask&style=flat-square) ![Gemini](https://img.shields.io/badge/Model-gemini--1.5--flash-orange?style=flat-square) ![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

<table>
<tr>
<td align="center"><picture>
   <source srcset="assets/screenshots/placeholder_main_light.svg" type="image/svg+xml"/>
   <img src="assets/screenshots/placeholder_main_light.png" alt="Main UI Light" width="320"/>
</picture><br/><sub>Main Interface (Light)</sub></td>
<td align="center"><img src="assets/screenshots/placeholder_chat_light.png" alt="Chat View Light" width="320"><br/><sub>Active Chat (Light)</sub></td>
</tr>
</table>
<sub><em>Add your real screenshots in <code>assets/screenshots</code> (keep same filenames).</em></sub>

</div>

---

## � Why This Project Exists
I wanted a minimal, fast, open implementation of a modern AI chat—without React bloat, with real streaming, and with clean persona prompts you can actually extend. This is a foundation you can fork into your own product, portfolio piece, or internal tool.

## 💼 Résumé Snippet
Implemented a production‑grade multi‑persona AI chat platform (Flask + Gemini 1.5 Flash) featuring SSE token streaming, role‑based system prompts, dark/light theming, local persistence, intent shortcuts, and robust session/history management.

## ✨ Features
| Area | Highlights |
|------|-----------|
| Streaming | Server‑Sent Events (token-by-token) with graceful fallback |
| Personas | 5 curated roles (easily extendable) with system prompts |
| UX Polish | Auto‑resizing input, role switcher, theme toggle, typing cadence |
| Persistence | Hybrid session + localStorage (no cookie overflow) |
| Safeguards | Intent overrides for common meta queries (model / creators) |
| Extensibility | Centralized role config + clean prompt build path |

## 🧠 Architecture Snapshot
```
Frontend (static)
   ├─ chat.js        # UI logic + SSE stream parsing
   ├─ style.css      # Theme tokens & layout
   └─ index.html     # Template w/ role selector
Backend (Flask)
   ├─ app.py         # Routes: /chat, /chat/stream, intents
   ├─ config.py      # Roles, API key, limits
   └─ (Gemini SDK)   # google-generativeai
```

## 🚀 Get Running (5 Steps)
```bash
git clone https://github.com/himanshu-chauhan-stack/AI-Chatbot.git
cd AI-Chatbot
pip install -r requirements.txt
# set your key (option A)
setx GEMINI_API_KEY "YOUR_KEY_HERE"  # Windows (new shell after)
# or put it in config.py (option B)
python app.py
```
Visit: http://localhost:5000

## ⚙️ Config At A Glance
| Key | Where | Notes |
|-----|-------|-------|
| GEMINI_API_KEY | env or config.py | Auth token |
| AI_ROLES | config.py | Persona definitions |
| MAX_CHAT_HISTORY | config.py | Rolling memory window |
| /chat/stream | app.py | Primary SSE endpoint |

## 🛠 Tech Stack
| Layer | Tools |
|-------|------|
| Backend | Flask, google-generativeai |
| Frontend | Vanilla JS, Fetch API, SSE |
| Styling | Modern CSS (flex/grid, variables) |
| AI | Gemini 1.5 Flash |

## 🏎 Design Decisions
* SSE chosen over WebSockets for simplicity + native streaming.
* Role prompts centralized for maintainability.
* Intent shortcuts avoid pointless paid tokens.
* History trimming prevents runaway context size.

## 🧪 Handy Prompts To Try
| Goal | Prompt |
|------|--------|
| Model meta | Which model are you using? |
| Attribution | Who developed you? |
| Persona check | Act as a financial advisor (education only) and explain diversification. |
| Creativity | Give 3 novel sci‑fi plot hooks. |
| Elaboration | Explain how SSE differs from WebSockets. |

## 📂 Project Layout
```
backend/app.py        # Core Flask implementation
config.py             # API key + roles
static/js/chat.js     # Frontend logic
static/style.css      # Styles
templates/index.html  # Main template
docs/                 # GitHub Pages assets
assets/screenshots/   # (Add your PNGs)
```

## 🌐 Deploy Notes
Gunicorn example (Linux):
```bash
gunicorn -w 4 -k gthread -b 0.0.0.0:5000 app:app
```
Platform tips: set env var GEMINI_API_KEY; optionally add SECRET_KEY.

## 🔐 Security Basics
| Rule | Why |
|------|-----|
| Don’t expose API key client-side | Protect billing/quota |
| Rotate keys occasionally | Limit blast radius |
| Add auth if multi-user | Prevent misuse |
| Rate limit endpoints | Control costs |

## 🗺 Future Ideas
- Embedding memory / vector search
- Chat export (Markdown / PDF)
- File & image inputs
- Plugin/tool invocation layer
- Simple auth + saved threads

## 🐛 Quick Fix Table
| Symptom | Remedy |
|---------|--------|
| No output streaming | Check Network tab: /chat/stream status 200? |
| Empty AI reply | Key invalid / quota exhausted |
| UI glitches | Hard refresh / clear cache |
| History missing | localStorage cleared |

## 🤝 Contribute
Fork → branch → concise commits → PR with before/after screenshot. Keep code style minimal + readable.

## 🙌 Credits
Built by **Ritesh** & **Himanshu** with ❤️ using Flask + Gemini.

## 📄 License
MIT. Use freely; attribution appreciated.

## 📬 Optional Links
Add your LinkedIn / Portfolio / Twitter here.

---
> Tip: On a résumé: “Built a streaming multi‑persona AI chat (Gemini 1.5 Flash) with SSE, role prompt system, and persistence architecture.”
