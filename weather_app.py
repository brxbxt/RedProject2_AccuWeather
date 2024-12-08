import requests
import json

API_KEY = "hipMbZ8XD03CZM2O9xCunVPnR0XmpUgW"

def get_weather_data(latitude, longitude):
    url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    params = {
        "apikey": API_KEY,
        "q": f"{latitude},{longitude}",
        "language": "ru-ru"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        location_data = response.json()
        location_key = location_data['Key']
        current_conditions_url = f"http://dataservice.accuweather.com/forecasts/v1/hourly/1hour/{location_key}?apikey={API_KEY}&language=ru-ru&details=True"
        response = requests.get(current_conditions_url)
        response.raise_for_status()
        current_conditions_data = response.json()[0]
        return {
            "temperature": round((int(current_conditions_data['Temperature']['Value'])-32)*5/9, 1),
            "humidity": current_conditions_data['RelativeHumidity'],
            "wind_speed": round(int(current_conditions_data['Wind']['Speed']['Value'])/1.609, 2),
            "probability_of_precipitation": current_conditions_data['PrecipitationProbability']
        }

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None
    except (IndexError, KeyError) as e:
        print(f"Ошибка обработки данных JSON: {e}")
        return None

def check_bad_weather(temperature, wind_speed, precipitation_probability):
    if temperature < 0 or temperature > 35 or wind_speed > 50 or precipitation_probability > 70:
        return "bad"
    else:
        return "good"

latitude = 55.7687
longitude = 37.5888
weather_data = get_weather_data(latitude, longitude)

if weather_data:
    print(json.dumps(weather_data, indent=4))

print(check_bad_weather(-5, 10, 30))  # bad - низкая температура
print(check_bad_weather(40, 10, 30))  # bad - высокая температура
print(check_bad_weather(20, 60, 30))  # bad - сильный ветер
print(check_bad_weather(20, 10, 80))  # bad - высокая вероятность осадков
print(check_bad_weather(20, 10, 30))  # good - нормальные условия

