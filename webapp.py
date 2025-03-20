from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

# Charger les réponses du chatbot depuis le JSON
with open("resources/data.json", "r", encoding="utf-8") as file:
    chatbot_data = json.load(file)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_response", methods=["POST"])
def get_response():
    user_message = request.json["message"].lower()  # Convertir en minuscules
    response = chatbot_data.get(user_message, "Désolé, je ne comprends pas...")
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
