
import requests
import json
from datetime import timedelta
from yaml import safe_load

def import_config():
    with open('./config/config.yaml','r') as config:
        config=safe_load(config)
    return config


def get_weather(city,config):
    url_base=config["openweather"]['base_url']
    api_key = config["openweather"]['api_key']
    params = {
        'q':city,
        'appid':api_key,
        'units':'metric'
        }
    response = requests.get(url_base,params=params)
    data = response.json()
    
    return data

def format_data(data):
    
    formatted_data = {
        "City": data["city"]["name"],
        "Country": data["city"]["country"],
        "Forecast": []
    }

    
    for entry in data["list"]:
        forecast_entry = {
            "DateTime": entry["dt_txt"],
            "Temperature": entry["main"]["temp"],
            "Feels Like": entry["main"]["feels_like"],
            "Min Temperature": entry["main"]["temp_min"],
            "Max Temperature": entry["main"]["temp_max"],
            "Pressure": entry["main"]["pressure"],
            "Humidity": entry["main"]["humidity"],
            "Weather": entry["weather"][0]["description"],
            "Wind Speed": entry["wind"]["speed"],
            "Wind Direction": entry["wind"]["deg"]
        }
        formatted_data["Forecast"].append(forecast_entry)

    return formatted_data


def save_data_as_json(data,file_path):
    with open(file_path, "w") as json_file:
        json.dump(data, json_file, indent=4)



def get_cities_along_route(origin,destination,config):
    api_key = config["google_maps"]["api_key"]

    directions_url = config["google_maps"]["base_url_directions"]
    geocoding_url = config["google_maps"]["base_url_geocode"]


    params = {
            "origin": origin,
            "destination": destination,
            "key": api_key
                }


    response = requests.get(directions_url, params=params)
    directions_data = response.json()


    if directions_data["status"] == "OK":
        
        steps = directions_data["routes"][0]["legs"][0]["steps"]

        
        route_points = []
        for step in steps:
            route_points.append((step["end_location"]["lat"], step["end_location"]["lng"]))

        
        cities = []

        for point in route_points:
            lat, lng = point
            geocoding_params = {
                "latlng": f"{lat},{lng}",
                "key": api_key
            }
            geocoding_response = requests.get(geocoding_url, params=geocoding_params)
            geocoding_data = geocoding_response.json()
            
            if geocoding_data["status"] == "OK":
                for result in geocoding_data["results"]:
                    for component in result["address_components"]:
                        if "locality" in component["types"] and component["long_name"] not in cities:
                            cities.append(component["long_name"])
        return cities

def get_time_journey_to_city(origin, destination, config):
    index_route = "|".join([origin, destination])
    waypoints = get_cities_along_route(origin,destination,config)
    api_key = config["google_maps"]["api_key"]
    waypoints_str = "|".join(waypoints)
    directions_url = f"{config['google_maps']['base_url_directions']}?origin={origin}&destination={destination}&waypoints={waypoints_str}&departure_time=now&key={api_key}"
    response = requests.get(directions_url)
    directions = response.json()
    if directions['status'] == 'OK':
        
        time_acumullator = timedelta()

        
        arrival_data = []

        
        for i, leg in enumerate(directions["routes"][0]["legs"]):
            
            duration_in_seconds = leg["duration"]["value"]
            
            time_acumullator += timedelta(seconds=duration_in_seconds)
            end_address = leg["end_address"]

            
            end_location = leg["end_location"]
            lat = end_location["lat"]
            lon = end_location["lng"]

            if str(time_acumullator)=="0:00:00":
                arrival_data.append({
                    'route': index_route,
                    "city": end_address.split('-')[0][0:-1],
                    "latitude": lat,
                    "longitude": lon,
                    "duration_of_the_journey": str(time_acumullator)
                })

            else:
                arrival_data.append({
                        'route': index_route,
                        "city": end_address.split(',')[0],
                        "latitude": lat,
                        "longitude": lon,
                        "duration_of_the_journey": str(time_acumullator)
                    })

        return arrival_data
config = import_config()
cities=get_cities_along_route("campo mourão",'curitiba',config)
data = get_time_journey_to_city('campo mourao','curitiba',config)
save_data_as_json(data,'extract_data/trafic/arrive_time.json')
for city in cities:
    data=get_weather(city,config)
    data=format_data(data)
    save_data_as_json(data,f"extract_data/weather/weather_{city}.json")


