from flask import Flask, request, jsonify
import pandas as pd
import os

app = Flask(__name__)

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FORECAST_PATH = os.path.join(BASE_DIR, "sku_8_week_forecast.csv")
RISK_PATH = os.path.join(BASE_DIR, "sku_risk_scoring.csv")
# Load data
forecast_df = pd.read_csv(FORECAST_PATH)
risk_df = pd.read_csv(RISK_PATH)

# Convert forecast date
forecast_df["Week"] = pd.to_datetime(forecast_df["Week"])



@app.route("/", methods=["GET"])
def home():
    return jsonify({"service": "Project FORESIGHT Scoring Service","status": "running"})


@app.route("/predict", methods=["POST"])
def predict():

    data = request.get_json()

    if not data or "sku" not in data:
        return jsonify({"error": "Please provide a SKU."}), 400
    sku = data["sku"]

    # Check whether SKU exists
    if sku not in risk_df["SKU"].values:
        return jsonify({"error": f"SKU '{sku}' not found."}), 404

    # Get forecast
    sku_forecast = forecast_df[forecast_df["SKU"] == sku].copy()

    # Get risk information
    sku_risk = risk_df[risk_df["SKU"] == sku].iloc[0]
    forecast_result = []

    for _, row in sku_forecast.iterrows():
        forecast_result.append({"week": row["Week"].strftime("%Y-%m-%d"),"forecast": round(float(row["Forecast"]), 2)})

    response = {"sku": sku,"forecast": forecast_result,
                "stockout_risk": sku_risk["Stockout_Risk"],
                "overstock_risk": sku_risk["Overstock_Risk"],
                "recommended_action": sku_risk["Recommended_Action"],
                "priority": sku_risk["Priority"],"total_value_at_stake": round(
                float(sku_risk["Total_Value_at_Stake"]), 2)}
    return jsonify(response)

@app.route("/predict_batch", methods=["POST"])
def predict_batch():

    data = request.get_json()

    if not data or "skus" not in data:
        return jsonify({"error": "Please provide a list of SKUs."}), 400
    skus = data["skus"]

    if not isinstance(skus, list) or len(skus) == 0:
        return jsonify({"error": "skus must be a non-empty list."}), 400

    results = []
    invalid_skus = []

    for sku in skus:

        if sku not in risk_df["SKU"].values:
            invalid_skus.append(sku)
            continue

        sku_forecast = forecast_df[forecast_df["SKU"] == sku].copy()
        sku_risk = risk_df[risk_df["SKU"] == sku].iloc[0]
        forecast_result = []

        for _, row in sku_forecast.iterrows():
            forecast_result.append({"week": row["Week"].strftime("%Y-%m-%d"),
                "forecast": round(float(row["Forecast"]), 2)})

        results.append({"sku": sku,"forecast": forecast_result,"stockout_risk": sku_risk["Stockout_Risk"],
                        "overstock_risk": sku_risk["Overstock_Risk"],"recommended_action": sku_risk["Recommended_Action"],
                        "priority": sku_risk["Priority"],"total_value_at_stake": round(
                        float(sku_risk["Total_Value_at_Stake"]), 2)})

    return jsonify({"results": results,"invalid_skus": invalid_skus})

if __name__ == "__main__":
    app.run(debug=True)