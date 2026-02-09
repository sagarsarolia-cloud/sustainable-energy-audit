import os
import requests

def get_current_weather(city="Jaipur"):
    """
    Fetches current weather for a given city (default Jaipur as per user request).
    Returns a string context like "35°C, Sunny".
    """
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    if not api_key:
        return "Unknown (Weather API Key missing)"
        
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if response.status_code == 200:
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            return f"{temp}°C, {desc}"
        else:
            return f"Unknown (API Error: {data.get('message', 'N/A')})"
            
    except Exception as e:
        print(f"Weather API Error: {e}")
        return "Unknown (Connection Error)"
