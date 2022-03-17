import logging
import os
import requests

from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
import azure.functions as func


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Air Pollution API - HTTP trigger function processed a request.')

    # Get params
    lat = req.params.get('lat')
    lon = req.params.get('lon')
    
    # No location provided
    if not lat or not lon:
        return func.HttpResponse(
             'You must supply a lat and lon attribute.',
             status_code=400
        )

    # Get api key secret from azure key vault
    key_vault_name = os.environ['KEY_VAULT_NAME']
    key_vault_url = f'https://{key_vault_name}.vault.azure.net'

    credential = DefaultAzureCredential()
    client = SecretClient(vault_url=key_vault_url, credential=credential)

    secret_name = os.environ['OPENWEATHER_SECRET_NAME']
    retrieved_secret = client.get_secret(secret_name)
    api_key = retrieved_secret.value

    # Params valid, make request to open weather api
    weather_response = requests.get(
        f'http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}'
    )

    # OpenWeather API Call not successful
    if weather_response.status_code != 200:
        return func.HttpResponse(
            f'OpenWeather Air Pollution API\nError: {weather_response.status_code}',
            status_code=weather_response.status_code
        )
    
    # Success
    return func.HttpResponse(
        weather_response.content,
        mimetype='application/json'
    )
