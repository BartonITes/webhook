from flask import Flask, request, jsonify, send_file
import os
import csv

app = Flask(__name__)

@app.route('/')
def home():
    return "Dialogflow Webhook is live!"

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()

    # Extract user query and parameters
    query_text = req['queryResult'].get('queryText', '').strip()
    parameters = req['queryResult'].get('parameters', {})
    symptom = parameters.get('symptom', '')
    severity = parameters.get('severity', '')
    duration = parameters.get('duration', '')

    # Intent name check
    intent_name = req['queryResult']['intent'].get('displayName', '')
    if intent_name.lower() == "default fallback intent":
        log_unrecognized(query_text)
        fulfillment_text = (
            
        )
        return jsonify({"fulfillmentText": fulfillment_text})

    # Otherwise use triage classification
    triage_result = classify_triage(symptom.lower(), severity.lower(), duration.lower())

    if triage_result == "urgent":
        fulfillment_text = (
           
        )
    elif triage_result == "routine":
        fulfillment_text = (
           
        )
    else:
        fulfillment_text = (
           
        )

    return jsonify({"fulfillmentText": fulfillment_text})

# ---------- Utility: log unknown queries ----------
def log_unrecognized(text):
    filename = "unrecognized.csv"
    file_exists = os.path.isfile(filename)
    with open(filename, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["user_input"])  # header
        writer.writerow([text])
    print(f"[LOG] Unrecognized phrase saved: {text}")

# ---------- Utility: export CSV ----------
@app.route('/export', methods=['GET'])
def export():
    filename = "unrecognized.csv"
    if not os.path.exists(filename):
        return "No unrecognized inputs logged yet."
    return send_file(filename, as_attachment=True)

# ---------- Symptom triage ----------
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

# ---------- Run ----------
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
