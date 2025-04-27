import requests
from rich import print_json, print
import os
from dotenv import load_dotenv
from pathlib import Path
import csv
import pendulum

load_dotenv()

geo_url = os.getenv("GEO_URL")
weather_url = os.getenv("WEATHER_URL")
api_key = os.getenv("API_KEY")


class WeatherApp:
    def __init__(self, city_name):
        self.city_name = city_name
        self.api_key = api_key
        self.longitude = []
        self.latitude = []
        self.weather_forecast = []


    def get_geo_location(self):
        self.geo_params = {
            'q': self.city_name,
            'apikey': self.api_key
        }
        try:
            response = requests.get(f'{geo_url}', params=self.geo_params)
            response.raise_for_status()
            parsed_data = response.json()

            if not parsed_data:
                print(
                    f"[bold yellow]City '{self.city_name}' not found. Please check the spelling and try again.[/]")
                return

            self.longitude = parsed_data[0]['lon']
            self.latitude = parsed_data[0]['lat']
            return parsed_data
        except requests.exceptions.HTTPError as error:
            print(
                f"[bold red]HTTP error occurred:[/] {error} — Status code: {error}")
        except requests.exceptions.RequestException as error:
            print(f"There was an error: {error}")
            return

    def get_forecast(self):
        self.weather_params = {
            'lat': self.latitude,
            'lon': self.longitude,
            'apikey': self.api_key
        }

        try:
            response = requests.get(
                weather_url, params=self.weather_params)  # type: ignore
            response.raise_for_status()
            parsed_data = response.json()
            self.weather_forecast = parsed_data['list']
            return parsed_data['list']
        except requests.exceptions.HTTPError as error:
            print(
                f"[bold red]HTTP error occurred:[/] {error} — Status code: {error}")
        except requests.exceptions.RequestException as error:
            print(f"There was an error: {error}")
            return
        
    def create_weather_csv(self):
        if not self.weather_forecast:
            return
        
        path = Path(__file__).parent / f"{self.city_name}_weather_report.csv"
        with path.open('w', newline='') as file_object:
            writer = csv.writer(file_object)
            writer.writerow(["Date / Time", "Weather Description"])

            for entry in self.weather_forecast:
                datetime = entry['dt']
                description = entry['weather'][0]['description']

                pdt = pendulum.from_timestamp(datetime)

                writer.writerow([pdt.to_day_datetime_string(), description])



def main():
    print(f"Welcome to Enit Weather App!!")
    try:
        city_name = input("Enter a city name: ").strip()
        city = WeatherApp(city_name.lower())
        city_location = city.get_geo_location()
        # print(city_location)

        if not city_location:
            return
        
        city.get_forecast()

        city.create_weather_csv()


    except TypeError as error:
        print(f"Only strings a re accepted")


if __name__ == "__main__":
    main()
