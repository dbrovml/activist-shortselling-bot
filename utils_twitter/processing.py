#
import re

TICKER_REPATTERN = r"\$[a-zA-Z]*"

def extract_ticker(tweet, take_first_ticker=True):
    try:
        matched = re.findall(TICKER_REPATTERN, tweet)
        tickers = [tckr.replace("$", "") for tckr in matched if tckr != "$"]
    except:
        tickers = None
    if len(tickers) > 1:
        if take_first_ticker:
            ticker = tickers[0]
        else:
            raise Exception("Multiple tickers")
    else:
        ticker = tickers[0]
    return ticker


