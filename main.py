import os
from flask import Flask, request, jsonify
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenRouter client (single key for all models)
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    default_headers={"HTTP-Referer": "http://localhost:5000"}  # Required by OpenRouter
)

# ----------------------------
# Reusable functions for each LLM
# ----------------------------

def call_gemini(prompt: str):
    """Send prompt to Gemini via OpenRouter."""
    response = client.chat.completions.create(
        model="google/gemini-3-flash-preview",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def call_chatgpt(prompt: str):
    """Send prompt to ChatGPT via OpenRouter."""
    response = client.chat.completions.create(
        model="openai/gpt-5.2-chat",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def call_claude(prompt: str):
    """Send prompt to Claude via OpenRouter."""
    response = client.chat.completions.create(
        model="anthropic/claude-opus-4.5",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def generateAccuracy(sentence: str):
    accuracyChat = int (call_chatgpt('ONLY ANSWER WITH A SINGLE NUMBER. "' + sentence + '"' + ". You are a professional fact-checker. With a single number, determine how misleading this statement is on a scale of 0-100 (0 being undoubtedly true, 100 being undoubtedly false). If it is not a statement that can be true or false, return -1."))
    accuracyGemini = int (call_gemini('ONLY ANSWER WITH A SINGLE NUMBER. "' + sentence + '"' + ". You are a professional fact-checker. With a single number, determine how misleading this statement is on a scale of 0-100 (0 being undoubtedly true, 100 being undoubtedly false). If it is not a statement that can be true or false, return -1."))
    accuracyClaude = int (call_claude('ONLY ANSWER WITH A SINGLE NUMBER. "' + sentence + '"' + ". You are a professional fact-checker. With a single number, determine how misleading this statement is on a scale of 0-100 (0 being undoubtedly true, 100 being undoubtedly false). If it is not a statement that can be true or false, return -1."))
    if accuracyChat == -1 or accuracyGemini == -1 or accuracyClaude == -1:
        return -1
    else:
        return int ((accuracyChat + accuracyClaude + accuracyGemini) / 3)

def generateInsight(accuracy: int, sentence: str):
    insight = call_chatgpt('Dont format your answer, dont start with "because", and always start with "The statement". Provide a very brief insight as to why this statement: "' + sentence + '" would have an inaccuracy score of ' + str (accuracy) + ", where 0 is undoubtedly true, 100 is undoubtedly false, and -1 means it's not a statement (but refer to the score as 'N/A' instead of '-1'), as of January 2026.")
    return insight

# ----------------------------
# Flask routes
# ----------------------------

@app.route("/api/accuracy", methods=["POST"])
def accuracy_route():
    data = request.json
    sentence = data.get("sentence")
    if not sentence:
        return jsonify({"error": "Missing 'sentence' parameter"}), 400

    try:
        accuracy = generateAccuracy(sentence)
        return jsonify({"accuracy": accuracy})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/insight", methods=["POST"])
def insight_route():
    data = request.json
    sentence = data.get("sentence")
    accuracy = data.get("accuracy")

    if sentence is None or accuracy is None:
        return jsonify({"error": "Missing 'sentence' or 'accuracy' parameter"}), 400

    try:
        insight = generateInsight(accuracy, sentence)
        return jsonify({"insight": insight})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ----------------------------
# Run Flask app
# ----------------------------

if __name__ == "__main__":
    app.run(debug=True)

acc = generateAccuracy("Trump is dead")
print(acc)
print(generateInsight(acc, "Trump is dead"))