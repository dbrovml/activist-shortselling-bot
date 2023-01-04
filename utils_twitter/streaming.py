#
import requests
import json

RULES_URI = "https://api.twitter.com/2/tweets/search/stream/rules"
STREAMING_URI = "https://api.twitter.com/2/tweets/search/stream"


def create_headers(bearer_token):
    headers = {"Authorization": "Bearer {}".format(bearer_token)}
    return headers


def get_rules(headers):
    response = requests.get(RULES_URI, headers=headers)
    if response.status_code != 200:
        err_msg = f"Cannot get rules (HTTP {response.status_code}): {response.text}"
        raise Exception(err_msg)
    return response.json()


def delete_all_rules(headers, rules):
    if rules is None or "data" not in rules:
        return None
    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(RULES_URI, headers=headers, json=payload)
    if response.status_code != 200:
        err_msg = f"Cannot delete rules (HTTP {response.status_code}): {response.text}"
        raise Exception(err_msg)
    return "OK"


def set_rules(headers, rules):
    payload = {"add": rules}
    response = requests.post(RULES_URI, headers=headers, json=payload)
    if response.status_code != 201:
        err_msg = f"Cannot add rules (HTTP {response.status_code}): {response.text}"
        raise Exception(err_msg)
    return "OK"


def handle_stream(headers, listener, **kwargs):
    response = requests.get(STREAMING_URI, headers=headers, stream=True)
    if response.status_code != 200:
        err_msg = f"Cannot add rules (HTTP {response.status_code}): {response.text}"
        raise Exception(err_msg)
    print("Stream handling started...")
    listener(response, kwargs)