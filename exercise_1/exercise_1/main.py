import argparse
import datetime
import logging
from typing import List
import os

from coingecko_wrapper import CoinGeckoWrapper
from tqdm import tqdm

# Define the parser to get the parameters from the CLI
parser = argparse.ArgumentParser(description="Get parameters from CLI.")
parser.add_argument(
    "--date",
    type=str,
    help="Select the desired date to retrieve cryptos data. In case bulk_reprocess, this is the start_date",
    required=True,
)
parser.add_argument(
    "--coin",
    type=str,
    help="Select the desired coin to retrieve its price",
    required=True,
)
parser.add_argument(
    "--bulk_reprocess",
    type=bool,
    help="In case you want to retrieve more than 1 date",
    default=False,
)
parser.add_argument(
    "--end_date", type=str, help="Date until you want to retrieve data"
)
args = parser.parse_args()


# Define logger
logging.basicConfig(
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
    format="%(asctime)s [%(levelname)s] %(message)s",
)

logger = logging.getLogger(__name__)

BASE_OUTPUT_PATH = os.path.join(os.path.dirname(__file__), 'output')


def date_range(
    start_date: datetime.datetime, end_date: datetime.datetime
) -> List[datetime.datetime]:
    """
    A function to get all the dates between 2 defined dates.

    Args:
        start_date (datetime.datetime): first date from the sequence (included on the returned sequence)
        end_date (datetime.datetime): last date from the sequence (included on the returned sequence)

    Returns:
        List[datetime.datetime]: list of dates
    """
    delta = end_date - start_date
    days = [
        start_date + datetime.timedelta(days=i) for i in range(delta.days + 1)
    ]
    return days


def main():

    date = datetime.datetime.strptime(args.date, "%Y-%m-%d")
    coin = args.coin
    bulk_reprocess = args.bulk_reprocess

    if not bulk_reprocess:
        coin_gecko = CoinGeckoWrapper(coin)
        coin_gecko.fetch_api_data(date)
        coin_gecko.store_on_filesystem(
            f"{BASE_OUTPUT_PATH}/{date.date()}_{coin}.json"
        )

    else:
        if not args.end_date:
            raise ValueError("Please specify an end_date!")

        start_date = datetime.datetime.strptime(args.date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(args.end_date, "%Y-%m-%d")

        if start_date > end_date:
            raise ValueError("end_date should be greater than start_date!")

        dates = date_range(start_date, end_date)
        coin_gecko = CoinGeckoWrapper(coin)

        for date in tqdm(dates):
            coin_gecko.fetch_api_data(date)
            coin_gecko.store_on_filesystem(
                f"{BASE_OUTPUT_PATH}/{date.date()}_{coin}.json"
            )


if __name__ == "__main__":
    main()
