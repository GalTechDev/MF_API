import requests
from .utils import APIResponse

class APISession:
    api_key = ""
    authToken = ""

    def set_auth_token(token):
        response = requests.post(url="https://portail-api.meteofrance.fr/token", data={"grant_type":"client_credentials"}, headers={"Authorization": f"Basic {token}"})
        if response.status_code == 200:
            APISession.api_key = response.json().get("access_token")

    def renew_token():
        APISession.api_key = ""
        return APISession.api_key

    def get_api_key():
        return APISession.api_key

    def gen_headers():
        return {
            "Authorization": f"Bearer {APISession.get_api_key()}"
        }

    def get(url, params=None, **kwargs):
        if "headers" in kwargs:
            headers = kwargs.pop("headers")

        headers.update(APISession.gen_headers())
        
        response = requests.get(url, headers=headers, params=params, **kwargs)
        if response.status_code == 401:
            #Retry with new token
            APISession.renew_token()
            headers.update(APISession.gen_headers())
            response = requests.get(url, headers=headers, params=params, **kwargs)

        return APIResponse(response)