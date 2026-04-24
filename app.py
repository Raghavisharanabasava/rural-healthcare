from flask import Flask, request, jsonify
from flask_cors import CORS
import random

app = Flask(__name__)
# The 'origins' part ensures no browser blocks the connection
CORS(app, resources={r"/*": {"origins": "*"}})

# DETAILED CLINICAL DATABASE
KNOWLEDGE_BASE = {
    "child": {
        "respiratory": {
            "title": "Pediatric Respiratory Care (ಮಕ್ಕಳ ಉಸಿರಾಟದ ಆರೈಕೆ)",
            "eat": "Give warm moong-dal ganji or thin rice porridge. If breastfeeding, continue frequently to prevent dehydration. Use only warm water.",
            "not_eat": "Strictly avoid refrigerated milk, cold juices, sweets, or oily snacks. These increase mucus and make breathing harder for children.",
            "do": "Watch the chest closely. If the skin pulls in between the ribs (retractions), go to the hospital immediately. Keep the head elevated.",
            "audio": "ಮಗುವಿನ ಉಸಿರಾಟ ಗಮನಿಸಿ. ಬಿಸಿ ಬಿಸಿ ಬೇಳೆ ಗಂಜಿ ಅಥವಾ ಎದೆ ಹಾಲು ನೀಡಿ. ಉಸಿರಾಡಲು ಕಷ್ಟವಾದರೆ ತಕ್ಷಣ ಆಸ್ಪತ್ರೆಗೆ ಬನ್ನಿ.",
            "severity": "URGENT"
        },
        "digestive": {
            "title": "Pediatric Gastric Care (ಮಕ್ಕಳ ಜೀರ್ಣಕ್ರಿಯೆ ಯೋಜನೆ)",
            "eat": "Provide ORS (Salt-Sugar-Water) after every loose motion. Mashed banana or well-cooked curd rice is best for a child's stomach.",
            "not_eat": "No cow's milk, spicy curries, or sugary store-bought juices. These can worsen diarrhea and cause stomach cramps.",
            "do": "Check for sunken eyes or a dry tongue. If the child hasn't passed urine in 6 hours, take them to the clinic immediately.",
            "audio": "ಮಗುವಿಗೆ ಆಗಾಗ ಓ.ಆರ್.ಎಸ್ ದ್ರಾವಣ ಕುಡಿಸಿ. ಮಗು ಪದೆ ಪದೆ ವಾಂತಿ ಮಾಡುತ್ತಿದ್ದರೆ ತಡ ಮಾಡಬೇಡಿ.",
            "severity": "HIGH"
        }
    },
    "older": {
        "neuro": {
            "title": "Senior Neurological Check (ಹಿರಿಯರ ನರರೋಗ ತಪಾಸಣೆ)",
            "eat": "Sip on tender coconut water or warm lemon water with a pinch of salt. Keep meals soft like Idli or Ragi Ganji.",
            "not_eat": "Avoid heavy salt, oily pickles, or strong coffee which can spike blood pressure and worsen dizziness or confusion.",
            "do": "Sit down immediately. Check if the person can smile or speak clearly without slurring. Confusion in seniors is a danger sign.",
            "audio": "ಹಿರಿಯರಿಗೆ ತಲೆಸುತ್ತು ಬಂದಾಗ ಕೂಡಲೇ ಕುಳ್ಳಿರಿಸಿ. ಬಿಪಿ ಪರೀಕ್ಷಿಸಿ. ಒಬ್ಬರೇ ನಡೆಯಲು ಬಿಡಬೇಡಿ.",
            "severity": "URGENT"
        },
        "skin": {
            "title": "Senior Skin & Infection Care (ಹಿರಿಯರ ಚರ್ಮದ ಆರೈಕೆ)",
            "eat": "Increase intake of Vitamin C foods like citrus fruits or amla. Drink plenty of water to keep the skin hydrated from within.",
            "not_eat": "Avoid fermented foods or very spicy masalas which can sometimes trigger more itching or irritation.",
            "do": "Do not scratch the area. Keep it clean with mild soap and water. If there is pus or a foul smell, consult a doctor for antibiotics.",
            "audio": "ಚರ್ಮವನ್ನು ಸ್ವಚ್ಛವಾಗಿಡಿ. ತುರಿಸಬೇಡಿ. ಗಾಯದಲ್ಲಿ ಕೀವು ಕಂಡುಬಂದಲ್ಲಿ ತಕ್ಷಣ ವೈದ್ಯರನ್ನು ಭೇಟಿ ಮಾಡಿ.",
            "severity": "STABLE"
        }
    },
    "adult": {
        "general": {
            "title": "Adult General Recovery (ವಯಸ್ಕರ ಚೇತರಿಕೆ ಯೋಜನೆ)",
            "eat": "Eat steamed vegetables, warm vegetable soups, and protein-rich foods like sprouts. Drink 3 liters of warm water today.",
            "not_eat": "Avoid junk food, carbonated sodas, and heavy spices until you feel fully recovered and energetic.",
            "do": "Take complete physical rest for 24 hours. Monitor your temperature and stay in a well-ventilated room.",
            "audio": "ಚೆನ್ನಾಗಿ ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ. ಬಿಸಿ ಆಹಾರ ಸೇವಿಸಿ. ಹಬೆಯಲ್ಲಿ ಬೇಯಿಸಿದ ತರಕಾರಿ ಉತ್ತಮ.",
            "severity": "STABLE"
        }
    }
}

@app.route('/rural-triage', methods=['POST'])
def triage():
    try:
        data = request.get_json()
        text = data.get('text', '').lower()
        age = data.get('age', 'adult')
        
        # CATEGORIZATION LOGIC
        cat = "general"
        if any(k in text for k in ['breath', 'cough', 'cold', 'ಕೆಮ್ಮು', 'ಉಸಿರಾಟ']): cat = "respiratory"
        elif any(k in text for k in ['stomach', 'vomit', 'loose', 'ಹೊಟ್ಟೆ']): cat = "digestive"
        elif any(k in text for k in ['head', 'dizzy', 'faint', 'ತಲೆಸುತ್ತು']): cat = "neuro"
        elif any(k in text for k in ['skin', 'rash', 'itch', 'ಚರ್ಮ']): cat = "skin"

        age_group = KNOWLEDGE_BASE.get(age, KNOWLEDGE_BASE['adult'])
        plan = age_group.get(cat, KNOWLEDGE_BASE['adult']['general'])

        return jsonify({
            "status": plan["severity"],
            "title": plan["title"],
            "eat": plan["eat"],
            "not_eat": plan["not_eat"],
            "do": plan["do"],
            "audio": plan["audio"],
            "token": f"SAHAYA-{random.randint(1000, 9999)}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # host='0.0.0.0' is the secret for hackathons—it makes your server visible to other devices
    app.run(host='0.0.0.0', port=8000, debug=True)
    