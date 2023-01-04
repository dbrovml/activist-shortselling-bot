#
from copy import copy
import numpy as np
import requests
import json
import time
from urllib.parse import urljoin, urlencode
from datetime import datetime, timedelta


class MKTClient():
    """
    Manages connection to the API service and implements core
    methods necessary for automated trading.
    """

    def __init__(self, credentials: dict):
        """ 
        Connection credentials are required to authenticate with the API. 
        Credentials and API root endpoint must match the desired account type.
        """
        self._api_key = credentials["api_key"]
        self._user_login = credentials["user_login"]
        self._password = credentials["password"]
        self._accid = credentials["accid"]
        self._root_endpoint = credentials["root_endpoint"]
        self._login()
        self._set_local_headers()

    def _login(self):
        """ 
        Sends a login request using the credentials from the init.
        Receives headers and body containing session-specific credentials
        required to interact with the service. Sets common headers.
        """
        response = self._post(
            url="session",
            headers={
                "Content-Type": "application/json; charset=UTF-8",
                "Accept": "application/json; charset=UTF-8",
                "X-IG-API-KEY": self._api_key,
                "Version": "2"
            },
            payload={
                "identifier": self._user_login, 
                "password": self._password
            }
        )

        self._common_headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Accept": "application/json; charset=UTF-8",
            "X-IG-API-KEY": self._api_key,
            "X-SECURITY-TOKEN": response.headers["X-SECURITY-TOKEN"],
            "CST": response.headers["CST"]
        }

    def _set_local_headers(self):
        """
        Given session-specific common_headers, sets "local" headers
        for each method by updating the API version parameter.
        """
        self._headers_search_newscode = copy(self._common_headers)
        self._headers_get_market_from_epic = copy(self._common_headers)
        self._headers_get_account_balance = copy(self._common_headers)
        self._headers_get_positions = copy(self._common_headers)

        self._headers_search_newscode.update({"Version": "1"})
        self._headers_get_market_from_epic.update({"Version": "3"})
        self._headers_get_account_balance.update({"Version": "1"})
        self._headers_get_positions.update({"Version": "2"})

    def _get(self, url, headers, params):
        """
        Parses the full url and sends a GET request.
        """
        response = requests.get(
            url=urljoin(self._root_endpoint, url),
            headers=headers, 
            params=params
        )
        if response.status_code != 200:
            err_msg = f"Error({response.status_code}): {response.text}"
            raise Exception(err_msg)
        return response

    def _post(self, url, headers, payload):
        """
        Parses the full url and sends a POST request.
        """
        response = requests.post(
            url=urljoin(self._root_endpoint, url),
            headers=headers, 
            json=payload
        )
        if response.status_code != 200:
            err_msg = f"Error({response.status_code}): {response.text}"
            raise Exception(err_msg)
        return response
    
    def _delete(self, url, headers, payload):
        """
        Parses the full url and sends a DELETE request.
        """
        response = requests.delete(
            url=urljoin(self._root_endpoint, url),
            headers=headers, 
            json=payload
        )
        if response.status_code != 200:
            err_msg = f"Error({response.status_code}): {response.text}"
            raise Exception(err_msg)
        return response

    def _put(self, url, headers, payload):
        """
        Parses the full url and sends a PUT request.
        """
        response = requests.put(
            url=urljoin(self._root_endpoint, url),
            headers=headers, 
            json=payload
        )
        if response.status_code != 200:
            err_msg = f"Error({response.status_code}): {response.text}"
            raise Exception(err_msg)
        return response

    def _get_market_from_epic(self, epic):
        """
        Gets market details given an epic identificator.
        """
        response_market = self._get(
            url=f"markets/{epic}",
            headers=self._headers_get_market_from_epic,
            params=None
        )
        return response_market.json()

    def _get_market_from_newscode(self, newscode):
        """
        Searches service database for a key-word term. Used for finding 
        an internal "epic" identificator and details for a given newscode.
        """
        response_market_search = self._get(
            url = "markets",
            headers=self._headers_search_newscode,
            params={"searchTerm": newscode}
        )
        matching_markets = response_market_search.json()["markets"]
        if len(matching_markets) != 1:
            err_msg = f"Error({len(matching_markets)}): nonunique result."
            raise Exception(err_msg)
        return self._get_market_from_epic(matching_markets[0]['epic'])

    def _get_positions(self):
        """
        Fetches the list ofopen positions for the current account
        and saves it as an internal attribute.
        """
        response = self._get(
            url="positions",
            headers=self._headers_get_positions,
            params=None
        )
        return response.json()["positions"]

    def _get_position_from_deal_reference(self, deal_reference, silent_fail=False):
        """
        Updates the internal attribute of open positions,
        scans it and fetches a specific deal_reference.
        """
        positions_list = self._get_positions()
        match = None
        for pos in positions_list :
            if pos["position"]["dealReference"] == deal_reference:
                match = pos
                return match
        if match is None:
            if silent_fail:
                return None
            else:
                err_msg = f"Error(): position not found, silent_fail=False"
                raise Exception(err_msg)

    def _get_account_balance(self):
        """
        Fetches current account status (balance, deposit, P/L).
        """
        response = self._get(
            url="accounts",
            headers=self._headers_get_account_balance,
            params=None
        )
        response = response.json()
        for acc in response["accounts"]:
            if acc["accountId"] == self._accid:
                return acc["balance"]
            else:
                pass

    def make_draft_position_from_newscode(self, newscode):
        """
        Returns a DraftPosition object populated with market
        details and local headers from the MKTClient instance.
        """
        market = self._get_market_from_newscode(newscode)
        return DraftPosition(self, market)

    def make_draft_position_from_epic(self, epic):
        """
        Returns a DraftPosition object populated with market
        details and local headers from the MKTClient instance.
        """
        market = self._get_market_from_epic(epic)
        return DraftPosition(self, market)




class DraftPosition(MKTClient):
    """
    Wraps the functionality needed to parse position
    specification and open a position. Inherits get/post/delete/put 
    and general methods from parent MKTClient instance.
    """

    def __init__(self, mclient, market):
        """
        Initializes a DraftPosition instance for a given market.
        Requires parent MKTClient instance to inherit headers
        from.
        """
        self._mcl = mclient
        self._market = market
        self._inherit_headers()
        self._set_local_headers()

        self._set_default_position_specification()

    def _inherit_headers(self):
        """
        Inherits common headers from parent MKTClient instance.
        """
        self._root_endpoint = self._mcl._root_endpoint
        self._accid = self._mcl._accid

        self._common_headers = self._mcl._common_headers
        self._headers_get_market_from_epic = self._mcl._headers_get_market_from_epic
        self._headers_get_account_balance = self._mcl._headers_get_account_balance
        self._headers_get_positions = self._mcl._headers_get_positions

    def _set_local_headers(self):
        """
        Given session-specific common_headers, sets "local" headers
        for each method by updating the API version parameter.
        """
        self._headers_manage_position = copy(self._common_headers)
        self._headers_close_position = copy(self._common_headers)

        self._headers_manage_position.update({"Version": "2"})
        self._headers_close_position.update({"Version": "1"})
        self._headers_close_position.update({"_method": "DELETE"})

    def _calculate_position_size(self, allocation_percentage=0.05):
        """
        Given margin details and last seen high price of the instrument, 
        calculates position size w.r.t. to set account balance allocation percentage.
        """
        avaiable_funds = self._get_account_balance()["available"]
        margin_factor = self._market["instrument"]["marginFactor"]
        high = self._market["snapshot"]["high"]
        leveraged_available_funds = avaiable_funds / (margin_factor / 100.0)
        return int(leveraged_available_funds * allocation_percentage / high)

    def _set_default_position_specification(self):
        """
        Parses position specification dictionary required to open
        a position.
        """
        self._default_position_specification = {
            "epic": self._market["instrument"]["epic"],
            "direction": "SELL",
            "size": self._calculate_position_size(),
            "level": None,
            "stopLevel": None,
            "stopDistance": None,
            "trailingStop": None,
            "trailingStopIncrement": None,
            # 
            "orderType": "MARKET", "timeInForce": "FILL_OR_KILL",
            "forceOpen": "true", "limitLevel": None,
            "limitDistance": None, "guaranteedStop": "false",
            "quoteId": None, "currencyCode": "USD", "expiry": "-"
        }

    def _set_position_trailing_stop_rules(self, trailing_stop_rules):
        """
        Sends a PUT request to update specification of a newly opened
        position.
        """
        level = self._position["position"]["level"]
        min_step_distance_p = self._market["dealingRules"]["minStepDistance"]["value"]
        min_stop_distance_pct = (
            self._market["dealingRules"]["minNormalStopOrLimitDistance"]["value"]
        )
        min_stop_distance_p = level * (min_stop_distance_pct / 100.0) + 20

        our_trailing_stop_distance_pct = trailing_stop_rules["trailingStopDistance"]
        our_step_distance_pct = trailing_stop_rules["trailingStep"]
        our_trailing_stop_distance_p = level * our_trailing_stop_distance_pct
        our_step_distance_p = level * our_step_distance_pct

        self._trailing_stop_request = {
            "trailingStop": True,
            "trailingStopDistance": max(our_trailing_stop_distance_p, min_stop_distance_p),
            "trailingStopIncrement": max(our_step_distance_p, min_step_distance_p),
            "stopLevel": trailing_stop_rules["stopLevel"] * level
            # "limitLevel": trailing_stop_rules["limitLevel"] * level
        }

        response = self._put(
            url=urljoin("positions/", f"otc/{self._position['position']['dealId']}"),
            headers=self._headers_manage_position,
            payload=self._trailing_stop_request
        )

    def _check_position_specification(self):
        """
        Verifies the parameters of an open position match the specification
        provided at the position opening.
        """
        requested_specification = {
            **self._default_position_specification, 
            **self._trailing_stop_request
        }
        executed_specification = {
            **self._position["position"], 
            **self._position["market"]
        }
        
        err = False
        for param in [
            "size", "direction", "epic", "trailingStopDistance", 
            "stopLevel", "limitLevel"
        ]:
            if requested_specification[param] != executed_specification[param]:
                err = param
        if (
            requested_specification["trailingStopIncrement"] 
            != executed_specification["trailingStep"]
        ):
            err = param

        if err:
            self.close_position()
            raise Exception(f"Position closed due to param mismatch: {err}.")

    def open_position(self, trailing_stop_rules=None, exit_rules=None):
        """
        Opens a position with given parameters provided in position specification. 
        Verifies the successful opening by looking up the returned dealReference in 
        the list of open positions. Returns an OpenPosition object.
        """
        response = self._post(
            url=urljoin("positions/", "otc"),
            headers=self._headers_manage_position,
            payload=self._default_position_specification
        )
        deal_reference = response.json()["dealReference"]
        self._position = self._get_position_from_deal_reference(deal_reference)
        self._set_position_trailing_stop_rules(trailing_stop_rules)
        self._position = self._get_position_from_deal_reference(deal_reference)
        self._check_position_specification()
        return OpenPosition(self, exit_rules=exit_rules)

    def close_position(self):
        """
        Closes the position.
        """
        response = self._post(
            url=urljoin("positions/", "otc"),
            headers=self._headers_close_position,
            payload={
                "dealId": self._position["position"]["dealId"],
                "size": self._position["position"]["size"],
                "direction": "BUY",
                "orderType": "MARKET"
            }
        )
        deal_reference = response.json()["dealReference"]
        position = self._get_position_from_deal_reference(deal_reference, True)
        if position is not None:
            err_msg = f"Error: position failed to close."
            raise Exception(err_msg)


class OpenPosition(DraftPosition):
    """
    Wraps the functionality needed to manage a open single position,
    e.g. monitoring and closing.
    """

    def __init__(self, draft_position, exit_rules=None):
        """
        Requires DraftPosition instance to inherit open position
        specification and headers.
        """
        self._dp = draft_position
        self._market = self._dp._market
        self._position = self._dp._position
        self._exit_rules = exit_rules
        self._inherit_headers()
        self._set_local_headers()

    def _inherit_headers(self):
        """
        Inherits common headers from parent MKTClient instance.
        """
        self._root_endpoint = self._dp._root_endpoint
        self._accid = self._dp._accid
        self._common_headers = self._dp._common_headers
        self._headers_manage_position = self._dp._headers_manage_position
        self._headers_get_positions = self._dp._headers_get_positions
        self._headers_close_position = self._dp._headers_close_position

    def _update_position_state(self):
        """
        Calls position from reference and updates self._position state.
        """
        deal_reference = self._position["position"]["dealReference"]
        self._position = self._get_position_from_deal_reference(deal_reference)
