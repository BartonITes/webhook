from flask import Flask, request, jsonify

app = Flask(__name__)

# Helper function to classify severity
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
        return 5  # default
    return 5

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json()

    parameters = req['queryResult']['parameters']
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


if __name__ == '__main__':
    app.run(debug=True)
