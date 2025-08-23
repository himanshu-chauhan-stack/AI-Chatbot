from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
import google.generativeai as genai
import datetime
import os
import webbrowser
import json
import threading
import time
from config import api_key, AI_ROLES, DEFAULT_AI_ROLE


app = Flask(__name__, template_folder="../templates", static_folder="../static")
CORS(app)

genai.configure(api_key=api_key)

def ai(prompt, system_prompt=None):
    """Call Gemini for general queries"""
    model = genai.GenerativeModel("gemini-1.5-flash")
    if system_prompt:
        full_prompt = f"{system_prompt}\n\nUser: {prompt}"
    else:
        full_prompt = prompt
    response = model.generate_content(full_prompt)
    return response.text


@app.route("/")
def index():
    return render_template("index.html", ai_roles=AI_ROLES)


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)
    message = data.get("message", "")
    ai_role = data.get("ai_role", DEFAULT_AI_ROLE)
    role_cfg = AI_ROLES.get(ai_role, AI_ROLES[DEFAULT_AI_ROLE])
    try:
        lm = message.lower()
        if ("model" in lm) and ("which" in lm or "what" in lm or "use" in lm or "using" in lm):
            answer = "gemini 1.5 flash"
        elif ("who" in lm) and ("developed" in lm or "made" in lm or "created" in lm) and ("you" in lm or "assistant" in lm):
            answer = "Ritesh and Himanshu"
        else:
            answer = ai(message, role_cfg["system_prompt"])
        return jsonify({
            "response": answer,
            "ai_role": ai_role,
            "role_name": role_cfg["name"]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/chat/stream", methods=["POST"])
def chat_stream():
    """Server-Sent Events streaming endpoint for real-time token output."""
    data = request.get_json(force=True)
    message = data.get("message", "")
    ai_role = data.get("ai_role", DEFAULT_AI_ROLE)
    role_cfg = AI_ROLES.get(ai_role, AI_ROLES[DEFAULT_AI_ROLE])

    # Use generate_content with safety: stream via .generate_content with stream=True
    lm = message.lower()
    override = None
    if ("model" in lm) and ("which" in lm or "what" in lm or "use" in lm or "using" in lm):
        override = "gemini 1.5 flash"
    elif ("who" in lm) and ("developed" in lm or "made" in lm or "created" in lm) and ("you" in lm or "assistant" in lm):
        override = "Ritesh and Himanshu"

    def generate():
        try:
            if override is not None:
                yield f"data: {json.dumps({'delta': override})}\n\n"
                yield f"data: {json.dumps({'done': True, 'response': override, 'ai_role': ai_role, 'role_name': role_cfg['name']})}\n\n"
                return
            model = genai.GenerativeModel("gemini-1.5-flash")
            prompt = f"{role_cfg['system_prompt']}\n\nUser: {message}"
            stream = model.generate_content(prompt, stream=True)
            accumulated = []
            for chunk in stream:
                if not hasattr(chunk, 'text'):
                    continue
                text = chunk.text
                if not text:
                    continue
                accumulated.append(text)
                payload = {"delta": text}
                yield f"data: {json.dumps(payload)}\n\n"
            final = ''.join(accumulated)
            yield f"data: {json.dumps({'done': True, 'response': final, 'ai_role': ai_role, 'role_name': role_cfg['name']})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate(), mimetype="text/event-stream")

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    query = data.get("query", "").lower()
    answer = ""
    open_url = None

    # Simple command handling
    sites = {
        "youtube": "https://www.youtube.com",
        "google": "https://www.google.com",
        "wikipedia": "https://wikipedia.com",
        "linkedin": "https://linkedin.com",
        "instagram": "https://instagram.com",
        "github": "https://github.com"
    }
    for name, url in sites.items():
        if f"open {name}" in query:
            open_url = url
            answer = f"Opening {name.capitalize()}..."
            try:
                webbrowser.open(open_url)
            except Exception:
                pass
            break

    if not answer:
        if "the time" in query:
            hour = datetime.datetime.now().strftime("%H")
            minute = datetime.datetime.now().strftime("%M")
            answer = f"Sir, the time is {hour} bajke {minute} minutes"
        else:
            answer = ai(query)

    return jsonify({"answer": answer, "open_url": open_url})

if __name__ == "__main__":
    app.run(debug=True)
