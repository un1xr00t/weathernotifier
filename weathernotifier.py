import requests
import json
import os
from datetime import datetime, timedelta

# Weatherbit API setup
api_key = 'your_weatherbit_api_key'  # Replace with your actual API key
lat = 'your_latitude'  # Replace with your latitude
lon = 'your_longitude'  # Replace with your longitude
location_name = 'your_location_name'  # Replace with your location name
weatherbit_url = f"https://api.weatherbit.io/v2.0/forecast/daily?lat={lat}&lon={lon}&key={api_key}&days=3"

# Pushover API setup
pushover_api_token = 'your_api_token'  # Replace with your actual Pushover API token
pushover_user_key = 'your_user_key'  # Replace with your actual Pushover user key
pushover_url = 'https://api.pushover.net/1/messages.json'

alert_log_file = 'weather_alert_log.json'
debug_log_file = 'debug_log.txt'

def send_pushover_notification(message, priority=0, retry=None, expire=None):
    data = {
        'token': pushover_api_token,
        'user': pushover_user_key,
        'message': message,
        'priority': priority
    }
    if retry is not None:
        data['retry'] = retry
    if expire is not None:
        data['expire'] = expire
    requests.post(pushover_url, data=data)

def load_alert_log():
    if os.path.exists(alert_log_file):
        with open(alert_log_file, 'r') as file:
            return json.load(file)
    return {}

def save_alert_log(alert_log):
    with open(alert_log_file, 'w') as file:
        json.dump(alert_log, file)

def log_debug(message):
    with open(debug_log_file, 'a') as file:
        file.write(f"{datetime.now()}: {message}\n")

def should_alert(alert_log, date, condition):
    alert_key = f"{date}-{condition}"
    last_alert_time = alert_log.get(alert_key)
    if last_alert_time:
        last_alert_time = datetime.fromisoformat(last_alert_time)
        if datetime.now() - last_alert_time < timedelta(days=1):  # Ensure no repeat alerts for the same condition within 24 hours
            log_debug(f"Alert skipped for {condition} on {date}: Last alert time was {last_alert_time}")
            return False
    return True

def update_alert_log(alert_log, date, condition):
    alert_key = f"{date}-{condition}"
    alert_log[alert_key] = datetime.now().isoformat()
    save_alert_log(alert_log)

def has_condition_changed(alert_log, date, new_condition):
    condition_key = f"{date}-last_condition"
    last_condition = alert_log.get(condition_key)
    if last_condition != new_condition:
        alert_log[condition_key] = new_condition
        save_alert_log(alert_log)
        log_debug(f"Condition changed for {date}: {new_condition}")
        return True
    return False

# Load previous alerts log
alert_log = load_alert_log()

# Fetch forecast data
try:
    response = requests.get(weatherbit_url)
    response.raise_for_status()  # Raise an error for bad status codes
    forecast_data = response.json()
except requests.exceptions.RequestException as e:
    error_message = f"Error fetching weather data: {e}"
    print(error_message)
    send_pushover_notification(error_message)
    log_debug(error_message)
    forecast_data = None
except json.JSONDecodeError as e:
    error_message = f"Error decoding weather data: {e}"
    print(error_message)
    send_pushover_notification(error_message)
    log_debug(error_message)
    forecast_data = None

# Check forecast for high temperatures and severe weather
if forecast_data:
    for day in forecast_data['data']:
        date = day['datetime']
        temp_max = day['max_temp']
        weather_conditions = day['weather']['description'].lower()

        log_debug(f"Processing forecast for {date}: {weather_conditions} with max temp {temp_max}°F")

        # Check for high temperatures (e.g., above 90°F)
        if temp_max > 90:
            if should_alert(alert_log, date, 'high_temp') or has_condition_changed(alert_log, date, 'high_temp'):
                message = f"Alert! The temperature in {location_name} is forecasted to exceed 90°F on {date}: High of {temp_max}°F"
                send_pushover_notification(message)
                log_debug(f"Sent high temp alert: {message}")
                update_alert_log(alert_log, date, 'high_temp')

        # Check for severe weather alerts, prioritizing tornadoes
        if 'tornado' in weather_conditions:
            if should_alert(alert_log, date, 'tornado') or has_condition_changed(alert_log, date, 'tornado'):
                message = f"URGENT: Tornado Alert for {location_name} on {date}: {weather_conditions}"
                send_pushover_notification(
                    message,
                    priority=2,  # Highest priority
                    retry=60,  # Retry every 60 seconds
                    expire=3600  # Expire after 1 hour
                )
                log_debug(f"Sent tornado alert: {message}")
                update_alert_log(alert_log, date, 'tornado')
        elif any(keyword in weather_conditions for keyword in ['thunderstorm', 'severe']):
            if should_alert(alert_log, date, weather_conditions) or has_condition_changed(alert_log, date, weather_conditions):
                message = f"Severe Weather Alert for {location_name} on {date}: {weather_conditions}"
                send_pushover_notification(message)
                log_debug(f"Sent severe weather alert: {message}")
                update_alert_log(alert_log, date, weather_conditions)

        # Check for rain warnings
        if any(keyword in weather_conditions for keyword in ['rain']):
            if should_alert(alert_log, date, weather_conditions) or has_condition_changed(alert_log, date, weather_conditions):
                message = f"Rain Alert for {location_name} on {date}: {weather_conditions}"
                send_pushover_notification(message)
                log_debug(f"Sent rain alert: {message}")
                update_alert_log(alert_log, date, weather_conditions)

print("Weather forecast check complete.")
log_debug("Weather forecast check complete.")
