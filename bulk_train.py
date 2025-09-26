import os
import csv
from google.cloud import dialogflow_v2 as dialogflow

# 1. Set Google Service Account JSON
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "path/to/service-account.json"

# 2. Dialogflow project ID
PROJECT_ID = "YOUR_PROJECT_ID"

# 3. Initialize client
client = dialogflow.IntentsClient()
parent = dialogflow.AgentsClient.agent_path(PROJECT_ID)

# 4. Load CSV
csv_file = "intents.csv"
intents_dict = {}

with open(csv_file, "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        intent_name = row["intent"]
        phrase = row["phrase"]
        response = row["response"]

        if intent_name not in intents_dict:
            intents_dict[intent_name] = {"phrases": [], "responses": set()}
        intents_dict[intent_name]["phrases"].append(phrase)
        intents_dict[intent_name]["responses"].add(response)

# 5. Create intents
for intent_name, data in intents_dict.items():
    training_phrases = []
    for phrase in data["phrases"]:
        part = dialogflow.Intent.TrainingPhrase.Part(text=phrase)
        training_phrases.append(dialogflow.Intent.TrainingPhrase(parts=[part]))

    messages = []
    for resp in data["responses"]:
        text = dialogflow.Intent.Message.Text(text=[resp])
        messages.append(dialogflow.Intent.Message(text=text))

    intent = dialogflow.Intent(
        display_name=intent_name,
        training_phrases=training_phrases,
        messages=messages
    )

    response = client.create_intent(request={"parent": parent, "intent": intent})
    print(f"Created intent: {response.display_name}")
