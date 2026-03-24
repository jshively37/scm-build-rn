import json
import os
import requests
import yaml

from dotenv import load_dotenv

BASE_AUTH_URL = "https://auth.apps.paloaltonetworks.com/auth/v1/oauth2/access_token"
URL_ENDPOINTS = {
    "ike_crypto_profiles": "https://api.strata.paloaltonetworks.com/config/network/v1/ike-crypto-profiles",
    "ipsec_crypto_profiles": "https://api.strata.paloaltonetworks.com/config/network/v1/ipsec-crypto-profiles",
    "ike_gateways": "https://api.strata.paloaltonetworks.com/config/network/v1/ike-gateways",
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


def get_profiles(url_endpoint):
    endpoint = f"{url_endpoint}?folder={FOLDER}"
    response = requests.request("GET", endpoint, headers=HEADERS)
    return response.json()


def create_ike_crypto_profile(ike_crypto_profile, url_endpoint):
    payload = json.dumps(
        {
            "name": ike_crypto_profile["name"],
            "folder": ike_crypto_profile["folder"],
            "hash": [
                ike_crypto_profile["hash"],
            ],
            "encryption": [ike_crypto_profile["encryption"]],
            "dh_group": [ike_crypto_profile["dh_group"]],
            "lifetime": {"seconds": ike_crypto_profile["lifetime_seconds"]},
        }
    )
    response = requests.request("POST", url_endpoint, headers=HEADERS, data=payload)
    print(response.text)


def create_ipsec_crypto_profile(ipsec_crypto_profile, url_endpoint):
    payload = json.dumps(
        {
            "name": ipsec_crypto_profile["name"],
            "folder": ipsec_crypto_profile["folder"],
            "lifetime": {"seconds": ipsec_crypto_profile["lifetime_seconds"]},
            "esp": {
                "encryption": [ipsec_crypto_profile["encryption_algorithm"]],
                "authentication": [ipsec_crypto_profile["hash"]],
            },
        }
    )
    response = requests.request("POST", url_endpoint, headers=HEADERS, data=payload)
    print(response.text)


def create_ike_gateway(ike_gateway, url_endpoint):
    payload = json.dumps(
        {
            "name": ike_gateway["name"],
            "folder": ike_gateway["folder"],
            "authentication": {
                "pre_shared_key": {"key": ike_gateway["pre_shared_key"]}
            },
            "peer_address": {"ip": ike_gateway["peer_address"]},
            "protocol": {
                "ikev2": {
                    "ike_crypto_profile": ike_gateway["ike_crypto_profile"],
                }
            },
        }
    )
    response = requests.request("POST", url_endpoint, headers=HEADERS, data=payload)
    print(response.text)


if __name__ == "__main__":
    create_token()
    with open(INPUT_FILE, "r") as f:
        data = yaml.safe_load(f)
    ike_crypto_profiles = get_profiles(URL_ENDPOINTS["ike_crypto_profiles"])
    ike_crypto_names = [item["name"] for item in ike_crypto_profiles["data"]]

    ipsec_crypto_profiles = get_profiles(URL_ENDPOINTS["ipsec_crypto_profiles"])
    ipsec_crypto_names = [item["name"] for item in ipsec_crypto_profiles["data"]]

    ike_gateways = get_profiles(URL_ENDPOINTS["ike_gateways"])
    ike_gateways_names = [item["name"] for item in ike_gateways["data"]]

    for ike_crypto_profile in data["ike_crypto_profiles"]:
        if ike_crypto_profile["name"] not in ike_crypto_names:
            create_ike_crypto_profile(
                ike_crypto_profile, URL_ENDPOINTS["ike_crypto_profiles"]
            )
        else:
            print(f"{ike_crypto_profile['name']} already exists, skipping creation.")

    for ipsec_crypto_profile in data["ipsec_crypto_profiles"]:
        if ipsec_crypto_profile["name"] not in ipsec_crypto_names:
            create_ipsec_crypto_profile(
                ipsec_crypto_profile, URL_ENDPOINTS["ipsec_crypto_profiles"]
            )
        else:
            print(f"{ipsec_crypto_profile['name']} already exists, skipping creation.")

    for ike_gateway in data["ike_gateways"]:
        if ike_gateway["name"] not in ike_gateways_names:
            create_ike_gateway(ike_gateway, URL_ENDPOINTS["ike_gateways"])
        else:
            print(f"{ike_gateway['name']} already exists, skipping creation.")
