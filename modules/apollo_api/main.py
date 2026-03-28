# import modules.constants as const
import requests
import json
import os


api_key = os.getenv('APOLLO_API_KEY')
base_url = "https://api.apollo.io/api/v1/contacts/search"

def api_call(query):
    """
    Consumes the apollo api
    needs a query in url format
    """

    global base_url
    global api_key

    headers = {
        "accept": "application/json",
        "Cache-Control": "no-cache",
        "Content-Type": "application/json",
        "x-api-key": api_key
    }

    response = requests.post(url, headers=headers)

    response_json = json.loads(response.text)

    print(response_json)