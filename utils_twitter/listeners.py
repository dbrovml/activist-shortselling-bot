#
from .processing import extract_ticker
import json
from datetime import datetime


def extract_basics(line):
    response_json = json.loads(line)
    tid = response_json["data"]["id"]
    text = response_json["data"]["text"]
    ticker = extract_ticker(text)
    timeline = response_json["matching_rules"][0]["tag"]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  
    response_dict = {
        "tid": tid, "text": text, "ticker": ticker,
        "timeline": timeline, "timestamp": timestamp
    }
    return response_dict


def listener_a(response, kwargs):
    for response_line in response.iter_lines():
        if response_line:
            response_dict = extract_basics(response_line)
            outpath = (
                kwargs["local_path"] 
                + response_dict["timeline"] 
                + "___"
                + response_dict["tid"]
            )
            print(response_dict)
            with open(f"{outpath}.txt", "w") as out:
                json.dump(response_dict, out)