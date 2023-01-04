#
from utils_platform.config import credentials_demo
from utils_platform.mclient import MKTClient
import json
import time


mclient = MKTClient(credentials_demo)
draft_position = mclient.make_draft_position_from_newscode("BTC")


trailing_stop_rules = {
    "trailingStop": True,
    "trailingStopDistance": 0.023,
    "trailingStep": 0.01,
    "stopLevel": 1.05,
    "limitLevel": None
}

open_position = draft_position.open_position(trailing_stop_rules)
open_position.monitor()
