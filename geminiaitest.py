import google.generativeai as genai
from config import api_key  


genai.configure(api_key=api_key)


model = genai.GenerativeModel("gemini-1.5-flash")


resp = model.generate_content([
    "Web development"
])


print(resp.text)
