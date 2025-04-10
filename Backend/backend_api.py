# app.py
import logging
import datetime
import random
import json
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from terra.base_client import Terra
from config import Config
from models.terra_client import TerraClient
from models.data_generator import DataGenerator


logging.basicConfig(level=logging.INFO)
_LOGGER = logging.getLogger("app")


app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Terra client
terra_client = TerraClient(
    api_key=Config.TERRA_API_KEY,
    dev_id=Config.TERRA_DEV_ID,
    webhook_secret=Config.TERRA_WEBHOOK_SECRET
)

# Mock data generation
data_generator = DataGenerator()


hr_samples_global = []
hr_index = 0

@app.route("/consumeTerraWebhook", methods=['POST'])
def consume_terra_webhook():
    """Handle incoming webhooks from Terra API"""
    body = request.get_json()
    _LOGGER.info("Got the Terra Webhook: %s", body)
    return Response(status=200)

@app.route("/authenticate", methods=['GET'])
def authenticate():
    """Generate authentication widget for Garmin"""
    widget_response = terra_client.generate_widget_session(providers=['GARMIN'], reference_id='1234')
    widget_url = widget_response.get_json()['url']
    return Response(
        f"<button onclick=\"location.href='{widget_url}'\">Authenticate with GARMIN</button>", 
        mimetype='text/html'
    )

@app.route('/getSleep', methods=['GET'])
def get_sleep():
    """Get sleep data for a specific user and date range"""
    sleep_data = terra_client.get_sleep_data(
        user_id=Config.DEFAULT_USER_ID,
        start_date=datetime.datetime(2025, 2, 5),
        end_date=datetime.datetime(2025, 2, 6)
    )
    
    _LOGGER.info("Sleep Data: %s", sleep_data)
    return jsonify(sleep_data)

@app.route('/getSleepScore', methods=['GET'])
def get_sleep_score():
    """Get sleep score for a specific user and date range"""
    sleep_score = terra_client.get_sleep_score(
        user_id=Config.DEFAULT_USER_ID,
        start_date=datetime.datetime(2025, 2, 5),
        end_date=datetime.datetime(2025, 2, 6)
    )
    
    _LOGGER.info("Sleep Score: %s", sleep_score)
    return jsonify(sleep_score)

@app.route('/getStressScore', methods=['GET'])
def get_stress_score():
    """Get stress score for a specific user and date range"""
    stress_score = terra_client.get_stress_score(
        user_id=Config.DEFAULT_USER_ID,
        start_date=datetime.datetime(2025, 2, 5),
        end_date=datetime.datetime(2025, 2, 6)
    )
    
    _LOGGER.info("Stress Score: %s", stress_score)
    return jsonify(stress_score)

@app.route('/getRespiratoryScore', methods=['GET'])
def get_respiratory_score():
    """Get respiratory score for a specific user and date range"""
    respiratory_score = terra_client.get_respiratory_score(
        user_id=Config.DEFAULT_USER_ID,
        start_date=datetime.datetime(2025, 2, 5),
        end_date=datetime.datetime(2025, 2, 6)
    )
    
    _LOGGER.info("Respiratory Score: %s", respiratory_score)
    return jsonify(respiratory_score)

@app.route('/getImmuneIndex', methods=['GET'])
def get_immune_index():
    """Get immune index for a specific user and date range"""
    immune_index = terra_client.get_immune_index(
        user_id=Config.DEFAULT_USER_ID,
        start_date=datetime.datetime(2025, 2, 5),
        end_date=datetime.datetime(2025, 2, 6)
    )
    
    _LOGGER.info("Immune Index: %s", immune_index)
    return jsonify(immune_index)

@app.route('/getActivity', methods=['GET'])
def get_activity():
    """Get activity data for a specific user and date range"""
    # Using mock data generator instead of real data
    activity_records = data_generator.generate_mock_activity_data(days=168)
    
    _LOGGER.info("MOCK Activity Data Generated: %s", activity_records)
    
    weekly_activity = data_generator.calculate_weekly_averages(activity_records)
    
    _LOGGER.info("Weekly Activity Averages: %s", weekly_activity)
    return jsonify(weekly_activity)

@app.route('/getHRSamples', methods=['GET'])
def get_hr_samples():
    """Get heart rate samples for a specific user and date range"""
    start_time = datetime.datetime(2025, 2, 10).replace(tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2025, 2, 15).replace(tzinfo=datetime.timezone.utc)
    
    hr_samples = terra_client.get_hr_samples(
        user_id=Config.DEFAULT_USER_ID,
        start_time=start_time,
        end_time=end_time
    )
    
    if not hr_samples:
        _LOGGER.warning("No HR samples found for the given time range.")
        return jsonify({"error": "No activity data found."}), 404
    
    return jsonify(hr_samples)

@app.route('/getHeartMetrics', methods=['GET'])
def get_heart_metrics():
    """Get heart metrics for a specific user and date range"""
    heart_metrics = terra_client.get_heart_metrics(
        user_id=Config.DEFAULT_USER_ID,
        start_date=datetime.datetime(2025, 2, 5),
        end_date=datetime.datetime(2025, 2, 6)
    )
    
    _LOGGER.info("Heart Metrics: %s", heart_metrics)
    return jsonify(heart_metrics)

@app.route('/getOxySaturation', methods=['GET'])
def get_oxy_saturation():
    """Get oxygen saturation data for a specific user and date range"""
    oxy_saturation = terra_client.get_oxygen_saturation(
        user_id=Config.DEFAULT_USER_ID,
        start_date=datetime.datetime(2025, 2, 5),
        end_date=datetime.datetime(2025, 2, 6)
    )
    
    _LOGGER.info("Avg Oxygen Saturation: %s", oxy_saturation)
    return jsonify(oxy_saturation)

@app.route('/initializeHRSamples', methods=['GET'])
def initialize_hr_samples():
    """Fetch and store HR samples in a global variable"""
    global hr_samples_global, hr_index
    
    start_time = datetime.datetime(2025, 2, 10).replace(tzinfo=datetime.timezone.utc)
    end_time = datetime.datetime(2025, 2, 15).replace(tzinfo=datetime.timezone.utc)
    
    hr_samples = terra_client.get_raw_hr_samples(
        user_id=Config.DEFAULT_USER_ID,
        start_time=start_time,
        end_time=end_time
    )
    
    if not hr_samples:
        _LOGGER.warning("No activity data found for the given time range.")
        return jsonify({"error": "No activity data found."}), 404
    
    # Convert timestamps to datetime objects for easier tracking
    hr_samples_global = [
        {
            "timestamp": datetime.datetime.fromisoformat(sample["timestamp"].replace("Z", "+00:00")),
            "bpm": sample["bpm"]
        }
        for sample in hr_samples
    ]
    
    # Reset index
    hr_index = 0
    
    _LOGGER.info("Initialized %d HR samples.", len(hr_samples_global))
    return jsonify({"message": f"Loaded {len(hr_samples_global)} heart rate samples."})

@app.route('/getNextHR', methods=['GET'])
def get_next_hr():
    """Returns the next HR sample based on global index"""
    global hr_samples_global, hr_index
    
    if not hr_samples_global:
        return jsonify({"error": "HR data not initialized. Call /initializeHRSamples first."}), 400
    
    # Ensure index stays within range
    if hr_index >= len(hr_samples_global):
        hr_index = len(hr_samples_global) - 1  # Stay at last value
    
    hr_sample = hr_samples_global[hr_index]
    hr_index += 1  # Move to the next sample for the next call
    
    return jsonify(hr_sample)

if __name__ == "__main__":
    app.run()
