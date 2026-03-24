import json
import os
import requests
import yaml

from dotenv import load_dotenv

BASE_AUTH_URL = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"
URL_ENDPOINTS = {
    "ike_crypto_profiles": "https://api.strata.paloaltonetworks.com/config/network/v1/ike-crypto-profiles",
}

INPUT_FILE = "remote_networks.yaml"

HEADERS = {
    "Accept": "application/json",
}

FOLDER = "Remote Networks"

AUTH_HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Accept": "application/json",
}

load_dotenv()
TSG_ID = os.environ.get("TSG_ID")
CLIENT_ID = os.environ.get("CLIENT_ID")
SECRET_ID = os.environ.get("SECRET_ID")


def create_token():
    auth_url = f"{BASE_AUTH_URL}?grant_type=client_credentials&scope:tsg_id:{TSG_ID}"

    token = requests.request(
        method="POST",
        url=auth_url,
        headers=AUTH_HEADERS,
        auth=(CLIENT_ID, SECRET_ID),
    ).json()
    HEADERS.update({"Authorization": f'Bearer {token["access_token"]}'})


def get_ike_crypto_profiles(url_endpoint):
    endpoint = f"{url_endpoint}?folder={FOLDER}"
    response = requests.request("GET", endpoint, headers=HEADERS)
    return response.json()

def create_crypto_profile(ike_crypto_profile, url_endpoint):
    payload = json.dumps({
        "name": ike_crypto_profile["name"],
        "folder": ike_crypto_profile["folder"],
        "hash": [
            ike_crypto_profile["hash"],
        ],
        "encryption": [ike_crypto_profile["encryption"]],
        "dh_group": [ike_crypto_profile["dh_group"]],
        "lifetime": {"seconds": ike_crypto_profile["lifetime_seconds"]},
    })
    response = requests.request("POST", url_endpoint, headers=HEADERS, data=payload)
    print(response.text)


if __name__ == "__main__":
    create_token()
    with open(INPUT_FILE, "r") as f:
        data = yaml.safe_load(f)
    ike_crypto_profiles = get_ike_crypto_profiles(URL_ENDPOINTS["ike_crypto_profiles"])
    ike_crypto_names = [item['name'] for item in ike_crypto_profiles['data']]

    for ike_crypto_profile in data["ike_crypto_profiles"]:
        if ike_crypto_profile["name"] not in ike_crypto_names:
            create_crypto_profile(ike_crypto_profile, URL_ENDPOINTS["ike_crypto_profiles"])
