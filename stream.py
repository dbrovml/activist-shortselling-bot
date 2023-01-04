#
from utils_twitter.config import API_BEARER
from utils_twitter.config import listening_scope
from utils_twitter.streaming import create_headers
from utils_twitter.streaming import get_rules
from utils_twitter.streaming import delete_all_rules
from utils_twitter.streaming import set_rules
from utils_twitter.streaming import handle_stream
from utils_twitter.listeners import listener_a


if __name__ == "__main__":
    headers = create_headers(API_BEARER)
    current_rules = get_rules(headers)
    delete = delete_all_rules(headers, current_rules)
    set_ = set_rules(headers, listening_scope)
    handle_stream(headers, listener=listener_a, local_path="log_twitter/")
