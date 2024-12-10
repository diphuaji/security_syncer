# API_KEY='H1DRZMCWSVSD16Q5'
# API_KEY='demo'

import requests

class AlphaVantage:
    def __init__(self, key: str) -> None:
        self.key = key

    def listing_status(self)->bytes:
        """
        Return csv bytes
        """
        url = f'https://www.alphavantage.co/query?function=LISTING_STATUS&apikey={self.key}'
        r = requests.get(url)
        r.raise_for_status()
        return r.content

# replace the "demo" apikey below with your own key from https://www.alphavantage.co/support/#api-key
# url = f'https://www.alphavantage.co/query?function=EMA&symbol=IBM&interval=weekly&time_period=14&series_type=close&apikey={API_KEY}'
# r = requests.get(url)
# data = r.json()


# print(data)