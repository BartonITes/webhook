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

    # ---------------------------
    # 1. Check for knowledge base answers first
    # ---------------------------
    knowledge = req.get("queryResult", {}).get("knowledgeAnswers", {}).get("answers", [])
    if knowledge:
        kb_answer = knowledge[0]["answer"]

        # Extract only the clean answer
        if "\nA:" in kb_answer:
            kb_answer = kb_answer.split("\nA:")[1].split("\nQ:")[0].strip()

        return jsonify({"fulfillmentText": kb_answer})

    # ---------------------------
    # 2. Handle structured triage intents
    # ---------------------------
    parameters = req['queryResult']['parameters']
    intent_name = req['queryResult']['intent']['displayName']
    query_text = req['queryResult']['queryText']

    symptom = parameters.get('symptom', '')
    severity = parameters.get('severity', '')
    duration = parameters.get('duration', '')

    if intent_name not in ["Default Fallback Intent"]:  # use your intents
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
    # 3. Fallback to ChatGPT if no match
    # ---------------------------
    gpt_response = call_chatgpt(query_text)

    # Save unknown queries for training later
    save_unrecognised(query_text, gpt_response)

    return jsonify({"fulfillmentText": gpt_response})


# ---------------------------
# Helper: Call OpenAI ChatGPT
# ---------------------------
def call_chatgpt(user_input):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",   # or gpt-4 if enabled
            messages=[
                {"role": "system", "content": "You are a helpful medical assistant. Always remind users to consult a doctor for serious conditions."},
                {"role": "user", "content": user_input}
            ],
            max_tokens=200
        )
        return response["choices"][0]["message"]["content"].strip()
    except Exception as e:
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
