import requests
import os

base_url = 'https://api.millionverifier.com/api/v3/?api={0}&email={1}&timeout=10'

def verify_email(email:str) -> dict:
    """
    Verifies an email consuming the MillionVerifier API
    """

    try:
        global base_url
        api_key = os.getenv('MILLION_API_KEY')
        url = base_url.format(api_key, email)
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()
        return data
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connecting: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout Error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Something went wrong: {err}")

