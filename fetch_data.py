import logging
import requests


#https://api.covid19india.org/data.json
url = "https://api.open-meteo.com/v1/forecast"
param = {
    "latitude": 40.1157,
    "longitude": 83.1327,
    "current": "temperature_2m"

}

def main():
    logging.info("Starting...")
    url = ""
    response = requests.get(url, params=param)
    logging.info(response.text)
    logging.info("Done!")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main()
