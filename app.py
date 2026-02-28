import os
from flask import Flask, render_template, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

# Load .env in local dev (safe in production too)
load_dotenv()

app = Flask(__name__)

# Read OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API environment variable not set.")

client = OpenAI(api_key=OPENAI_API_KEY)


# -------------------------
# System Prompt for Zel-D
# -------------------------

SYSTEM_PROMPT = """
You are Zel-D’s official customer support assistant.

About Zel-D:
- Premium healthy nutrition brand.
- Offers probiotic drinks, protein drinks, and ready-to-eat clean meals.
- Uses cold-chain shipping.
- Products are perishable and require refrigeration.

Behavior Rules:
1. Be friendly, calm, and professional.
2. Keep answers concise and clear.
3. No medical diagnosis. Provide general wellness information only.
4. If asked about medical conditions, say:
   "For medical advice, please consult a licensed healthcare professional."
5. Do NOT invent prices, discounts, shipping regions, or policies.
   If unknown, say:
   "For the most accurate information, please contact support@zel-d.com."
6. If a user reports illness or adverse reaction:
   - Express empathy.
   - Suggest discontinuing use.
   - Recommend contacting a healthcare professional.
   - Escalate to support@zel-d.com.

Health Disclaimer:
Zel-D products support general wellness but are not intended to diagnose, treat, cure, or prevent any disease.

Escalation Behavior:
If a user asks about:
- Refund disputes
- Delivery damage
- Account/payment issues
- Allergic reactions
Always suggest contacting support@zel-d.com for direct assistance.

Tone:
Clean, modern, wellness-focused.
Supportive but not overly casual.
"""


# -------------------------
# Routes
# -------------------------

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/products")
def products():
    return render_template("products.html")


@app.route("/faq")
def faq():
    return render_template("faq.html")


# -------------------------
# Chat API
# -------------------------

@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json()

    if not data or "message" not in data:
        return jsonify({"reply": "Invalid request."}), 400

    user_message = data["message"]

    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            max_output_tokens=400,
            temperature=0.4
        )

        reply = response.output_text

        return jsonify({"reply": reply})

    except Exception as e:
        print("OpenAI error:", e)
        return jsonify({
            "reply": "Sorry, we're experiencing a temporary issue. Please email support@zel-d.com."
        }), 500


# -------------------------
# App Entry
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)