import requests
import json
from flask import Flask, render_template, request, jsonify

API_KEY = "hipMbZ8XD03CZM2O9xCunVPnR0XmpUgW"
LOCATIONS_FILE = "static/locations.json"

def load_locations():
    try:
        with open(LOCATIONS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_locations(locations):
    with open(LOCATIONS_FILE, "w", encoding="utf-8") as file:
        json.dump(locations, file, ensure_ascii=False, indent=4)

locations = load_locations()

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
            "Temperature": round((int(current_conditions_data['Temperature']['Value'])-32)*5/9, 1),
            "Humidity": current_conditions_data['RelativeHumidity'],
            "Wind speed": round(int(current_conditions_data['Wind']['Speed']['Value'])/1.609, 2),
            "Probability of precipitation": current_conditions_data['PrecipitationProbability']
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


def get_city_name_from_coordinates(latitude, longitude):
    url = "http://dataservice.accuweather.com/locations/v1/cities/geoposition/search"
    params = {
        "apikey": API_KEY,
        "q": f"{latitude},{longitude}",
        "language": "ru-ru"
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        city_name = data['ParentCity']['LocalizedName']
        return city_name
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при запросе к API: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Ошибка обработки данных JSON: {e}")
        return None

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_condition = None
    error_message = None
    overall_condition = None

    if request.method == 'POST':
        try:
            start_location = request.form['start_location']
            end_location = request.form['end_location']

            if start_location is None or end_location is None:
                raise ValueError("Не удалось получить координаты.")

            start_latitude, start_longitude = get_coordinates(start_location)
            end_latitude, end_longitude = get_coordinates(end_location)
            if start_latitude is None or start_longitude is None or end_latitude is None or end_longitude is None:
                raise ValueError("Не удалось получить координаты.")

            start_weather = get_weather_data(start_latitude, start_longitude)
            end_weather = get_weather_data(end_latitude, end_longitude)

            if start_weather is None:
                raise ValueError(
                    f"Ошибка получения данных о погоде для '{start_location}'. Возможно, проблема с API или сетью.")
            if end_weather is None:
                raise ValueError(
                    f"Ошибка получения данных о погоде для '{end_location}'. Возможно, проблема с API или сетью.")

            start_condition = check_bad_weather(start_weather['Temperature'], start_weather['Wind speed'], start_weather['Probability of precipitation'])
            end_condition = check_bad_weather(end_weather['Temperature'], end_weather['Wind speed'], end_weather['Probability of precipitation'])

            weather_condition = {
                "start": {"location": start_location, "condition": start_condition, "details": start_weather},
                "end": {"location": end_location, "condition": end_condition, "details": end_weather}
            }

            if start_condition == "bad" or end_condition == "bad":
                overall_condition = "Сейчас не время для путешествий!"
            else:
                overall_condition = "Можно отправляться!"

        except (KeyError, ValueError, requests.exceptions.RequestException) as e:
            error_message = f"Ошибка: {e}"

    return render_template('index.html', weather_condition=weather_condition, error_message=error_message, overall_condition=overall_condition)

@app.route('/add_city', methods=['GET', 'POST'])
def add_city():
    error_message = None
    success_message = None

    if request.method == 'POST':
        latitude = request.form['latitude']
        longitude = request.form['longitude']

        if latitude and longitude:
            try:
                latitude = float(latitude)
                longitude = float(longitude)

                city_name = get_city_name_from_coordinates(latitude, longitude)

                if city_name:
                    locations[city_name] = (latitude, longitude)
                    save_locations(locations)
                    success_message = f"Город {city_name} успешно добавлен!"
                else:
                    error_message = "Не удалось найти город по данным координатам."
            except ValueError:
                error_message = "Ошибка: координаты должны быть числовыми."
        else:
            error_message = "Ошибка: все поля должны быть заполнены."

    return render_template('add_city.html', locations=locations, error_message=error_message, success_message=success_message)

def get_coordinates(location_name):
    return locations.get(location_name)

if __name__ == '__main__':
    app.run(debug=True)