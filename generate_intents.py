import csv
import random

# List of symptoms/conditions with sample responses
symptoms = {
    "Fever": "I see you have a fever. How severe is it? (mild, moderate, severe)",
    "Cough": "I see you have a cough. How long has it lasted?",
    "Headache": "I see you have a headache. How severe is it?",
    "Emergency": "⚠️ This seems like an emergency. Please call emergency services immediately",
    "SoreThroat": "It seems you have a sore throat. Warm fluids and rest may help.",
    "ShortnessOfBreath": "⚠️ Shortness of breath may be serious. Seek medical attention if severe.",
    "Fatigue": "It seems you are fatigued. Rest and hydration are recommended.",
    "Nausea": "It seems you are feeling nauseous. Can you describe more about your symptoms?",
    "Vomiting": "It seems you are vomiting. Stay hydrated and rest. Seek medical help if severe.",
    "Diarrhea": "It seems you have diarrhea. Stay hydrated and monitor your condition.",
    "MuscleAches": "It seems you have muscle aches. Rest and hydration may help.",
    "Cold": "It seems you have a cold. Monitor symptoms and rest.",
    "Dizziness": "⚠️ Dizziness can be serious. Please rest and seek help if persistent.",
    "BackPain": "It seems you have back pain. Rest and gentle stretching may help.",
    "StomachAche": "It seems you have stomach pain. Monitor symptoms and rest.",
    "Rash": "It seems you have a skin rash. Avoid scratching and monitor.",
    "JointPain": "It seems you have joint pain. Rest and gentle exercises may help.",
    "Insomnia": "It seems you have sleep problems. Try relaxation techniques and sleep hygiene.",
    "Allergies": "It seems you may have allergies. Avoid triggers and monitor symptoms.",
    "HeartPalpitations": "⚠️ Heart palpitations can be serious. Monitor and seek help if severe."
}

# Variations to prepend or append to phrases
variations = [
    "I have",
    "I'm experiencing",
    "Feeling",
    "Suffering from",
    "Since yesterday I have",
    "For the past few days I have",
    "My body shows",
    "I noticed",
    "Lately I have",
    "Suddenly I have"
]

# Generate training phrases for each symptom
training_data = []
for symptom, response in symptoms.items():
    for _ in range(25):  # 25 variations per symptom → ~500 lines total
        phrase = random.choice(variations) + " " + symptom.lower().replace("Emergency", "chest pain")  # Emergency is chest pain
        training_data.append([symptom, phrase, response])

# Write to CSV
with open('intents.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(["intent", "phrase", "response"])
    writer.writerows(training_data)

print("intents.csv generated with", len(training_data), "lines.")
