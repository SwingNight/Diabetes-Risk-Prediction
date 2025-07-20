import os
import json
import pandas as pd
import joblib
import numpy as np
from chalice import Chalice, Response, CORSConfig
import traceback

app = Chalice(app_name='input')

# CORS config
cors_config = CORSConfig(
    allow_origin='http://127.0.0.1:5500', # Local development URL
    allow_headers=['Content-Type'],
    max_age=600,
    expose_headers=['Content-Type'],
    allow_credentials=True
)

# Paths
MODEL_PATH = 'model/xgb_model.pkl'
SCALER_PATH = 'model/scaler.pkl'
FEATURE_ORDER_PATH = 'model/feature.json'

# Load resources
try:
    model = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH)
    with open(FEATURE_ORDER_PATH, 'r') as f:
        feature_order = json.load(f)
    print("Model, scaler, and feature order loaded.")
except Exception as e:
    print("Failed to load model/scaler/feature order:", str(e))
    model = None
    scaler = None
    feature_order = None

@app.route('/predict', methods=['POST'], cors=cors_config)
def predict():
    if model is None or scaler is None or feature_order is None:
        return Response(body={'error': 'Model/scaler not loaded.'}, status_code=500)

    try:
        request = app.current_request
        raw_data = request.json_body
        print("Received input:", raw_data)

        # Convert to float, fill missing values with NaN
        cleaned = {
            key: float(value) if value not in ['', None] else np.nan
            for key, value in raw_data.items()
        }

        # Construct correct feature order
        input_df = pd.DataFrame([cleaned])
        input_df = input_df.reindex(columns=feature_order)

        # Fill missing values (optional)
        input_df.fillna(input_df.mean(numeric_only=True), inplace=True)

        # Scale input
        input_scaled = scaler.transform(input_df)

        # Predict
        proba = model.predict_proba(input_scaled)[0][1]
        prediction = int(proba >= 0.45)  # Use same threshold as training

        print(f"Prediction: {prediction}, Risk Score: {proba:.4f}")

        return Response(
            body={
                'prediction': prediction,
                'risk_score': round(float(proba), 4)
            },
            headers={
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST'
            }
        )

    except Exception as e:
        print("Internal error:", traceback.format_exc())
        return Response(body={'error': str(e)})
