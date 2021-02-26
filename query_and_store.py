import sqlalchemy
import os
import auxiliary
import requests
from typing import List, Union
import json
import logging
import types

"""
query cmc and store results in sqlite db.
api reference - https://coinmarketcap.com/api/documentation/v1/#operation/getV2CryptocurrencyInfo
"""

init_args = types.SimpleNamespace()
limit = 600
mode = "production"


def init(args: types.SimpleNamespace) -> None:
    """
    start point
    """
    global init_args
    init_args = args

    auxiliary.enable_logger("query_and_store", log_to_console=True)
    logging.info("script started")

    if db_init():
        cmc_data = cmc_query()
        db_insert_data(cmc_data)


def db_init() -> bool:
    """
    create a db or use existing
    """
    if os.path.isfile(init_args.db):
        return True
    else:
        engine = sqlalchemy.create_engine(f"sqlite:///{init_args.db}", echo=False)
        with engine.connect() as conn:
            conn.execute(
                sqlalchemy.text(
                    "CREATE TABLE db ( \
                    symbol TEXT, \
                    cmc_rank INTEGER, \
                    price REAL, \
                    name TEXT, \
                    last_updated TEXT)"
                )
            )
            return True


def cmc_query() -> List[dict]:
    """
    query cmc for data
    """
    connection_info = {
        "production": {
            "url": "https://pro-api.coinmarketcap.com",
            "api": auxiliary.get_conf()["cmc"]["pro"],
        },
        "sandbox": {
            "url": "https://sandbox-api.coinmarketcap.com",
            "api": auxiliary.get_conf()["cmc"]["sandbox"],
        },
    }

    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "deflate, gzip",
        "X-CMC_PRO_API_KEY": connection_info[mode]["api"],
    }
    url = f"{connection_info[mode]['url']}/v1/cryptocurrency/listings/latest?limit={limit}"
    r = requests.get(url, headers=headers)
    response = r.json()["data"]
    return response


def parse_cmc_data(i: json) -> Union[dict, bool]:
    """
    parse and validate data received from cmc before storing
    :return either all local variables or False if validation fails
    """
    name = i["name"]
    symbol = i["symbol"]
    price = i["quote"]["USD"]["price"]
    cmc_rank = i["cmc_rank"]
    last_updated = i["quote"]["USD"]["last_updated"].split("T")[0]  # leave only date

    if not isinstance(price, float):
        logging.error(f"bad price when fetching data: {locals()}")
        return False

    return locals()


def db_insert_data(cmc_data: List[dict]) -> None:
    """
    add cmc json list to db
    """
    if not cmc_data:
        print("nothing returned by cmc")
        exit(1)

    engine = sqlalchemy.create_engine(f"sqlite:///{init_args.db}", echo=False)
    with engine.connect() as conn:
        for i in cmc_data:
            if i_parsed := parse_cmc_data(i):
                conn.execute(
                    sqlalchemy.text(
                        "INSERT INTO db (name, symbol, price, cmc_rank, last_updated) \
                        VALUES (:name, :symbol, :price, :cmc_rank, :last_updated)"
                    ),
                    {
                        "name": i_parsed["name"],
                        "symbol": i_parsed["symbol"],
                        "price": i_parsed["price"],
                        "cmc_rank": i_parsed["cmc_rank"],
                        "last_updated": i_parsed["last_updated"],
                    },
                )
