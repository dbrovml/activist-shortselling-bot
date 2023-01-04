#
from .rest import tw_handle

import tweepy
import pandas as pd

attributes = [
    "created_at", "full_text", "id", 
    "retweet_count", "favorite_count"
]

def fetch_timeline(timeline):
    fetched = tweepy.Cursor(
        method=tw_handle.user_timeline, id=timeline, 
        tweet_mode='extended', include_rts=False, trim_user=True
    )
    tweet_dicts = []
    for tweet in fetched.items():
        tweet_dict = {}
        for attribute in attributes:
            tweet_dict[attribute] = getattr(tweet, attribute)
        tweet_dicts.append(tweet_dict)
    tweet_df = pd.DataFrame(tweet_dicts, columns=attributes)
    tweet_df["timeline"] = timeline
    return tweet_df

def fetch_timelines(timelines):
    tweet_dfs = []
    for timeline in timelines:
        tweet_df = fetch_timeline(timeline)
        tweet_dfs.append(tweet_df)
    return pd.concat(tweet_dfs)