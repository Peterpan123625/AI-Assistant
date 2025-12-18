import os
import requests 
from dotenv import load_dotenv

def get_weather(location=None):
    """Get weather information"""
    if not config.get("weather_api_key"):
        print("Weather API key not configured. Add WEATHER_API_KEY to .env")
        return True
    
    location = location or config.get("location", "Dallas")
    
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather"
        params = {
            "q": location,
            "appid": config["weather_api_key"],
            "units": "imperial" if config.get("temperature_unit") == "fahrenheit" else "metric"
        }
        
        response = requests.get(url, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            
            unit = "°F" if config.get("temperature_unit") == "fahrenheit" else "°C"
            
            weather_report = f"Weather in {location}: {description}. "
            weather_report += f"Temperature is {temp:.0f}{unit}, feels like {feels_like:.0f}{unit}. "
            weather_report += f"Humidity is {humidity}%."
            
            print(weather_report)
        else:
            print(f"Couldn't get weather for {location}.")
    
    except Exception as e:
        print(f"Error getting weather: {str(e)}")
    
    return True

config = {
    "location": "Johannesburg",  ## default location should be whatever the devices is located 

    "weather_api_key": "",
    "temperature_unit": "celsius",
    
}

load_dotenv()

weather_key = os.getenv("WEATHER_API_KEY")
if weather_key:
    config["weather_api_key"] = weather_key

get_weather()