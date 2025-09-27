from flask import Flask, request, jsonify
import os
import openai
import csv

app = Flask(__name__)

# 🔑 Load OpenAI API Key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return "Dialogflow Webhook is live with ChatGPT + Auto-learning!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()

    parameters = req['queryResult'].get('parameters', {})
    intent_name = req['queryResult']['intent']['displayName'].lower()
    query_text = req['queryResult'].get('queryText', '')

    # ---------------------------
    # 1. Knowledge base answer first
    # ---------------------------
    knowledge = req.get("queryResult", {}).get("knowledgeAnswers", {}).get("answers", [])
    if knowledge:
        kb_answer = knowledge[0]["answer"]
        if "\nA:" in kb_answer:
            kb_answer = kb_answer.split("\nA:")[1].split("\nQ:")[0].strip()
        if kb_answer.strip():  # If KB answer exists, return it
            return jsonify({"fulfillmentText": kb_answer})

    # ---------------------------
    # 2. Triage intents
    # ---------------------------
    triage_intents = ["triageintent1", "triageintent2"]  # replace with your triage intent names
    if intent_name in triage_intents:
        symptom = parameters.get('symptom', '')
        severity = parameters.get('severity', '')
        duration = parameters.get('duration', '')

        triage_result = classify_triage(symptom.lower(), severity.lower(), duration.lower())
        if triage_result == "urgent":
            fulfillment_text = (
                "Based on your symptoms, this may be urgent. "
                "I recommend seeking immediate medical attention. "
                "Would you like me to connect you to a medical assistant?"
            )
        elif triage_result == "routine":
            fulfillment_text = (
                "This doesn't appear to be an emergency. "
                "Would you like to schedule an appointment with a doctor?"
            )
        else:
            fulfillment_text = (
                "It seems like a mild condition. You can try resting and staying hydrated. "
                "Let me know if you'd like help with anything else."
            )
        return jsonify({"fulfillmentText": fulfillment_text})

    # ---------------------------
    # 3. Fallback → ChatGPT
    # ---------------------------
    gpt_response = call_chatgpt(query_text)
    save_unrecognised(query_text, gpt_response)
    return jsonify({"fulfillmentText": gpt_response})


# ---------------------------
# Helper: Call OpenAI ChatGPT
# ---------------------------
def call_chatgpt(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant. Always remind users to consult a doctor for serious conditions."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=250
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print("OpenAI Error:", e)
        return "Sorry, I couldn’t process your request right now."


# ---------------------------
# Helper: Auto-learning (log unknown queries)
# ---------------------------
def save_unrecognised(query, response):
    file_path = "unrecognised.csv"
    file_exists = os.path.isfile(file_path)
    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Query", "GPT_Response"])  # header
        writer.writerow([query, response])


# ---------------------------
# Helper: Triage Logic
# ---------------------------
def classify_triage(symptom, severity, duration):
    red_flags = ['chest pain', 'shortness of breath', 'dizziness']
    severity_score = extract_severity_score(severity)
    if symptom in red_flags and severity_score >= 7:
        return "urgent"
    elif severity_score <= 3 and "day" in duration.lower():
        return "selfcare"
    else:
        return "routine"

def extract_severity_score(severity):
    try:
        for token in severity.split():
            if token.isdigit():
                return int(token)
        if "mild" in severity:
            return 2
        elif "moderate" in severity:
            return 5
        elif "severe" in severity:
            return 8
    except:
        return 5
    return 5


# 🔧 Run app
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
