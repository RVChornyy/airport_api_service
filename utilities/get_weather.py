import os
import requests
from dotenv import load_dotenv

load_dotenv()

URL = "http://api.weatherapi.com/v1/current.json"

API_KEY = os.getenv("API_KEY")


def get_weather(city) -> str:
    response = requests.get(
        URL,
        params={
            "key": API_KEY,
            "q": city
        }
    )
    if response.status_code == 200:
        resp = response.json()
        return (f"{resp['location']['name']}/{resp['location']['country']}"
                f" {resp['location']['localtime']}"
                f" Weather: {resp['current']['temp_c']}"
                f" Celsius, {resp['current']['condition']['text']}")
    return "Sorry, weather service is not available"
