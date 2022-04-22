import datetime
import json
import logging

import requests

# Define logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)


class CoinGeckoWrapper:
    """
    A class to represent a crypto coin.

    Attributes:
        coin (str): name of the coin to lookup (eg: bitcoin)

    Methods:
        fetch_api_data(): gets the data retrieved from CoinGecko API for a given coin and a given date
    """

    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3/coins"

    def __init__(self, coin: str):
        self.coin = coin
        self.json_data = None

    def fetch_api_data(self, date: datetime.datetime) -> None:
        """
        Function to retrieve crypto data from CoinGecko API for a give coin and date.

        Args:
            date (datetime.datetime): ISO8601 date for which the prices of the interested coin should be lookup (eg: 2022-04-10)

        Returns:
            json_data (object): JSON response of the CoinGecko API for the desire coin and date.
        """
        formatted_date = date.strftime("%d-%m-%Y")
        URL = f"{self.COINGECKO_BASE_URL}/{self.coin}/history?date={formatted_date}"

        logger.info(
            f"Fetching {self.coin} data for the {date.date()} on {URL} ..."
        )
        resp = requests.get(URL)
        try:
            if resp.status_code == 200:
                data = resp.json()
                json_data = json.dumps(data)
                logger.info(f"Data retrieved OK")

            else:
                logger.error(
                    f"Error {resp.status_code} ({resp.reason}) while fetching {self.coin} data for the {date.date()} on {URL}"
                )
                logger.error(resp.text)
                raise ValueError(
                    f"Error while fetching {self.coin} data for the {date.date()} on {URL}"
                )
        except Exception as e:
            logger.error(
                f"Error while fetching {self.coin} data for the {date.date()} on {URL}"
            )
            logger.error(e)
            raise ValueError(
                f"Error while fetching {self.coin} data for the {date.date()} on {URL}"
            )

        self.json_data = json_data

    def store_on_filesystem(self, path: str) -> None:
        """Stores stores the CoinGecko API response on the filesystem

        Args:
            path (str): path where to store the CoinGecko API JSON response
        """
        if not self.json_data:
            raise ValueError(
                "Please execute .fetch_api_data(DATE) with the desired date!"
            )

        with open(path, "w") as file:
            file.write(self.json_data)
