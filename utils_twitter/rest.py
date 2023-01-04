#
import tweepy

def rest_handle(api_key, api_secret, access_token, access_secret):
    """
    Sets OAuth credentials in tweepy:
        (api_key, api_secret, access_token, access_secret)
    Opens and returns a tweepy api handler
    """
    auth = tweepy.OAuthHandler(api_key, api_secret)
    auth.set_access_token(access_token, access_secret)
    handle = tweepy.API(auth)
    return handle

if "tw_handle" not in globals():
    from .config import API_KEY, API_SECRET
    from .config import ACCESS_TOKEN, ACCESS_SECRET
    tw_handle = rest_handle(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_SECRET)

