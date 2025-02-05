from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Configure Gemini API Key
genai.configure(api_key="AIzaSyA1-xmhIdqyPfH_65nl8ucX8ATg_ja80uw")
model = genai.GenerativeModel("gemini-pro")

# Store conversation context
previous_query = ""
previous_car_model = ""  # To track the last car model mentioned

@app.route("/chat", methods=["POST"])
def chat():
    global previous_query, previous_car_model
    data = request.json
    user_query = data.get("query", "").strip()

    if not user_query:
        return jsonify({"error": "Query cannot be empty!"}), 400

    # Check if query is related to cars
    if is_car_related(user_query):
        previous_car_model = user_query  # Update car model if a direct car query
        previous_query = user_query  # Store full query for context tracking
        final_query = user_query
    elif is_follow_up_query(user_query):
        if previous_car_model:
            final_query = f"{previous_car_model} {user_query}"  # Link to last car model
        else:
            return jsonify({"response": "Please specify a car model first."})
    else:
        return jsonify({"response": "I only answer about cars."})

    # Create structured prompt
    prompt = f"""
    You are a car expert. Provide a structured response to the following car-related query:
    "{final_query}"

    Guidelines:
    - Include relevant specifications, comparisons, pricing, faults, and reviews if applicable.
    - Use bullet points or numbered lists for clarity.
    - Ensure responses are clear, concise, and well-structured.
    - If the query is unclear, ask for clarification.
    """

    # Generate response using Gemini API
    try:
        response = model.generate_content(prompt)
        return jsonify({"response": response.text})
    except Exception as e:
        return jsonify({"error": "Error generating response!", "details": str(e)}), 500

def is_car_related(query):
    """Checks if the query is related to a car model or general car topic."""
    car_keywords = [
        "car", "vehicle", "engine", "horsepower", "torque", "mileage", "fuel", "sedan", "SUV", 
        "hatchback", "truck", "Tesla", "Toyota", "Honda", "BMW", "Mercedes", "Audi", "Porsche", 
        "Ford", "Chevrolet", "Hyundai", "Kia", "Nissan", "Volkswagen", "electric car", "hybrid car", 
        "transmission", "brakes", "suspension", "tires", "wheels", "interior", "exterior", "safety",
        "features", "performance", "maintenance", "insurance", "leasing", "buying", "selling", "market",
        "dealership", "test drive", "modifications", "warranty", "crash test", "resale value", "charging",
        "battery", "autonomous", "self-driving", "camera", "sensors", "infotainment", "navigation",
        "connectivity", "sunroof", "alloy wheels", "headlights", "taillights", "adaptive cruise control",
        "lane assist", "blind spot monitoring", "parking assist", "drivetrain", "differential", "gearbox",
        "manual transmission", "automatic transmission", "CVT", "dual-clutch", "paddle shifters",
        "launch control", "acceleration", "top speed", "handling", "stability", "comfort", "noise",
        "vibration", "build quality", "reliability", "service interval", "spare parts", "tuning",
        "performance parts", "exhaust", "turbocharger", "supercharger", "rally racing", "drift", "track",
        "leaderboard", "rankings", "car awards", "concept cars", "prototype", "spy shots", "teasers",
        "leaks", "new car releases", "ownership review", "user reviews", "expert review", "buying guide",
        "car tips", "maintenance hacks", "DIY car fixes", "checklist", "specifications", "model year",
        "facelift", "update", "upgrade", "variant", "auction", "bidding", "car financing", "EMI",
        "loan options", "insurance claims", "road tax", "registration", "license plates",
    ]
    return any(keyword.lower() in query.lower() for keyword in car_keywords)

def is_follow_up_query(query):
    """Checks if the query is a follow-up related to a previously mentioned car model."""
    follow_up_keywords = [
        "price", "faults", "specs", "features", "review", "comparison", "tyre size", 
        "headlights", "paint quality", "fuel economy", "safety rating"
    ]
    return query.lower() in follow_up_keywords

if __name__ == "__main__":
    app.run(debug=True)
