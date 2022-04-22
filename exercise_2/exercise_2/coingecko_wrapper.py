import datetime
import json
import logging

import pandas as pd
import requests
from dateutil.relativedelta import relativedelta
from sqlalchemy.exc import IntegrityError
from sqlite_cli import SqLiteClient

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
        store_on_filesystem(): stores the CoinGecko API response on the filesystem
        insert_raw_data_on_db(): insert raw data on coin_raw PostgreSQL table
        upsert_aggreated_data_on_db(): upserts aggregated data on coin_aggregated PostgreSQL table
    """

    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3/coins"

    POSTGRES_DB = "postgres"
    POSTGRES_HOST = "mutt-db"  # "localhost"
    POSTGRES_USER = "postgres"
    POSTGRES_PASSWORD = "postgres"

    DB_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}/{POSTGRES_DB}"

    def __init__(self, coin: str):
        self.coin = coin
        self.date = None
        self.json_data = None

    def fetch_api_data(self, date: datetime.datetime) -> None:
        """
        Function to retrieve crypto data from CoinGecko API for a give coin and date.

        Args:
            date (datetime.datetime): ISO8601 date for which the prices of the interested coin should be lookup (eg: 2022-04-10)

        Returns:
            json_data (object): JSON response of the CoinGecko API for the desire coin and date.
        """
        self.date = date
        formatted_date = date.strftime("%d-%m-%Y")
        URL = f"{self.COINGECKO_BASE_URL}/{self.coin}/history?date={formatted_date}"

        logger.info(
            f"Fetching {self.coin} data for the {date.date()} on {URL} ..."
        )
        resp = requests.get(URL)
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

    def insert_raw_data_on_db(self) -> None:
        """A function to process and store the CoinGecko API response on coin_raw PostgreSQL table.

        That table has coin_id, date, price, response as columns.
        """
        if not self.json_data:
            raise ValueError(
                "Please execute .fetch_api_data(DATE) with the desired date!"
            )

        coin_raw_data = [
            [
                self.coin,
                self.date.date(),
                json.loads(self.json_data)["market_data"]["current_price"][
                    "usd"
                ],
                self.json_data,
            ]
        ]
        coin_raw_data_pd = pd.DataFrame(
            coin_raw_data, columns=["coin_id", "date", "price", "response"]
        )

        sql_cli = SqLiteClient(self.DB_URI)
        try:
            logger.info(
                f"Inserting {self.coin} data for {self.date.date()} on coin_raw table ..."
            )
            sql_cli.insert_from_frame(coin_raw_data_pd, "coin_raw")
        except IntegrityError:
            logger.info(
                f"Already have {self.coin} data for {self.date.date()} on DB"
            )
        except Exception as e:
            logger.info(f"Unknown error: {e}")

    def upsert_aggregated_data_on_db(self) -> None:
        """A function to process and store the CoinGecko API response on coin_aggregated PostgreSQL table.

        That table has coin_id, year_month, max_price, min_price as columns.
        """
        if not self.json_data:
            raise ValueError(
                "Please execute .fetch_api_data(DATE) with the desired date!"
            )

        current_moth = self.date.strftime("%Y-%m-01")
        following_month = (self.date + relativedelta(months=1)).strftime(
            "%Y-%m-01"
        )

        sql_cli = SqLiteClient(self.DB_URI)

        sql_cli.execute(
            f"""
            DELETE FROM coin_aggregated
            WHERE 
                coin_id = '{self.coin}' AND
                year_month = '{current_moth}'
            """
        )
        coin_aggregated_data = sql_cli.to_frame(
            f"""
            SELECT 
                coin_id,
                TO_CHAR(date, 'YYYY-MM-01') as year_month,
                MAX(price) as max_price,
                MIN(price) as min_price
            FROM coin_raw
            WHERE 
                coin_id = '{self.coin}' AND
                date >= '{current_moth}' AND
                date < '{following_month}'
            GROUP BY 1, 2
            """
        )

        try:
            logger.info(
                f"Upserting {self.coin} data for {current_moth} on coin_aggregated table ..."
            )
            sql_cli.insert_from_frame(coin_aggregated_data, "coin_aggregated")
        except Exception as e:
            logger.info(f"Unknown error: {e}")
