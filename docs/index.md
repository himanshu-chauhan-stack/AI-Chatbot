---
layout: default
title: AI Chat Assistant
---

<div align="center">
	<h1>🤖 AI Chat Assistant</h1>
	<p><strong>Real‑time multi‑persona chat powered by Google Gemini (gemini‑1.5‑flash)</strong></p>
	<p>
		<a href="../README.md">README</a> ·
		<a href="#live-demo">Live Demo</a> ·
		<a href="#features">Features</a> ·
		<a href="#setup">Setup</a>
	</p>
	<img src="preview-light.png" alt="Screenshot" style="max-width:720px;border:1px solid #e3e3e3;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.06);"/>
	<p><em>Add your own screenshot as <code>docs/preview-light.png</code> (optional dark variant <code>preview-dark.png</code>).</em></p>
</div>

---

<a id="live-demo"></a>
## ⚡ Live Demo / Deployment
GitHub Pages hosts this static landing page only. The Flask backend (real‑time streaming) must run on a server (Render / Railway / VPS / local). After you deploy the backend, set an environment variable or edit the front‑end JS to point to your API base URL.

Example hosted backend: `https://your-backend-domain.example`  
Front-end fetch target (in `static/js/chat.js`): `/chat` → replace with full URL if cross‑origin.

---

<a id="features"></a>
## ✨ Key Features
| Category | Highlights |
|----------|-----------|
| Real‑Time | SSE token streaming, typing indicator |
| Multi‑Persona | Teacher, Financial, Creative, Technical, General |
| UX | Dark/Light themes, auto‑expand input, responsive layout |
| Persistence | LocalStorage chat history, session trimming |
| Smart Intents | Built‑in replies for model & authors queries |
| Deployability | Minimal dependencies, docs site, production config tips |

---

<a id="setup"></a>
## 🛠 Quick Local Setup
```bash
git clone https://github.com/himanshu-chauhan-stack/AI-Chatbot.git
cd AI-Chatbot
pip install -r requirements.txt
python app.py
```
Browse: http://localhost:5000

Set your Gemini key in `config.py` (or export `GEMINI_API_KEY`).

---

## 🚀 GitHub Pages Activation (You Already Have /docs)
1. Open Repo → Settings → Pages.  
2. Source: Deploy from branch → Branch `main` / Folder `/docs`.  
3. Save → Wait for build (≈1 min).  
4. Site URL appears (copy & add to README badge if desired).  
5. (Optional) Custom domain: add it to Settings → Pages & put it in `docs/CNAME`.

### Optional Badge
Add to top of README after Pages is live:
```markdown
![Pages](https://img.shields.io/website?url=https%3A%2F%2Fhimanshu-chauhan-stack.github.io%2FAI-Chatbot%2F)
```

---

## 🔄 API URL Customization
If deploying front-end statically separate from backend domain, modify base:
```javascript
// In static/js/chat.js (example)
const API_BASE = 'https://your-backend.example';
fetch(`${API_BASE}/chat`, { /* ... */ })
```
Also enable CORS (already included) and set allowed origins if tightening security.

---

## 🧪 Test Prompts
| Goal | Prompt |
|------|--------|
| Model Check | Which model do you use? |
| Credits | Who developed you? |
| Persona Switch | Act as a teacher and explain photosynthesis. |
| Streaming | List 5 startup ideas; elaborate each. |

---

## ❤️ Credits
Made with <span style="color:#e25555">♥</span> by **Ritesh** & **Himanshu**.

---

_This page is generated via GitHub Pages (Jekyll: minima theme). Customize `_config.yml` or add `assets/css/custom.css` for deeper theming._
