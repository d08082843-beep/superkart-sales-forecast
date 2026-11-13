# Import necessary libraries
import joblib  # For loading the serialized model
import pandas as pd  # For data manipulation
from flask import Flask, request, jsonify  # For creating the Flask API

# Initialize the Flask application
superkart_api = Flask("SuperKart Sales Predictor")

# Load the trained pipeline (preprocessing + tuned Random Forest)
model = joblib.load("superkart_model.joblib")

# Features the model expects, in the same order used during training
FEATURES = [
    "Product_Weight",
    "Product_Sugar_Content",
    "Product_Allocated_Area",
    "Product_MRP",
    "Store_Size",
    "Store_Location_City_Type",
    "Store_Type",
    "Product_Id_char",
    "Store_Age_Years",
    "Product_Type_Category",
]


# Define a route for the home page (GET request)
@superkart_api.get("/")
def home():
    """Health check: confirms the API is up and running."""
    return "Welcome to the SuperKart Sales Prediction API!"


# Define an endpoint for single-record prediction (POST request)
@superkart_api.post("/v1/predict")
def predict_sales():
    """Predicts sales for one product-store record sent as JSON."""
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Request body must be JSON"}), 400

    # Check that every feature is present
    missing = [f for f in FEATURES if f not in data]
    if missing:
        return jsonify({"error": f"Missing features: {missing}"}), 400

    # Build a one-row DataFrame in the order the model was trained on
    sample = pd.DataFrame([{f: data[f] for f in FEATURES}])

    # Make the prediction
    prediction = model.predict(sample)[0]

    # Return the prediction as a JSON response
    return jsonify({"Predicted Sales": round(float(prediction), 2)})


# Define an endpoint for batch prediction (POST request with a CSV file)
@superkart_api.post("/v1/predictbatch")
def predict_sales_batch():
    """Predicts sales for every row of an uploaded CSV file."""
    if "file" not in request.files:
        return jsonify({"error": "Upload a CSV file under the key 'file'"}), 400

    # Read the uploaded CSV file into a DataFrame
    input_data = pd.read_csv(request.files["file"])

    missing = [f for f in FEATURES if f not in input_data.columns]
    if missing:
        return jsonify({"error": f"Missing columns: {missing}"}), 400

    # Make predictions for all rows
    predictions = model.predict(input_data[FEATURES])

    # Each key is the row index, each value the predicted sales for that row
    output = {str(i): round(float(p), 2) for i, p in enumerate(predictions)}
    return jsonify(output)


# Run the Flask app (used only when starting with `python app.py`; Docker uses gunicorn)
if __name__ == "__main__":
    superkart_api.run(host="0.0.0.0", port=7860, debug=False)
