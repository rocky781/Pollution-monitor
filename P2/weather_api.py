import requests

API_KEY = '7a6cfb01825070bd088b1eb5518fbb74'  # Get from https://home.openweathermap.org/api_keys

def get_weather(city):
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
    response = requests.get(url).json()
    
    if response.get("cod") != 200:  # If city not found
        return {"error": "City not found"}

    return {
        "temperature": response["main"]["temp"],
        "humidity": response["main"]["humidity"],
        "description": response["weather"][0]["description"],
    }

def get_pollution(city):
    geocode_url = f'http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={API_KEY}'
    geocode_response = requests.get(geocode_url).json()
    
    if not geocode_response:
        return {"error": "City not found"}
    
    lat, lon = geocode_response[0]['lat'], geocode_response[0]['lon']
    
    pollution_url = f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}'
    pollution_response = requests.get(pollution_url).json()

    return {
        "pm2_5": pollution_response["list"][0]["components"]["pm2_5"],
        "pm10": pollution_response["list"][0]["components"]["pm10"],
        "co": pollution_response["list"][0]["components"]["co"],
    }

