import sqlalchemy
import os
import auxiliary
import requests
from typing import List, Union
import logging
import types
import inspect

"""
query cmc and store results in sqlite db.
api reference - https://coinmarketcap.com/api/documentation/v1/#operation/getV1CryptocurrencyQuotesLatest
"""

init_args = types.SimpleNamespace()
limit = 700
mode = "production"


def main(args: types.SimpleNamespace) -> None:
    """
    start point
    """
    main_boilerplate(args)

    # pre-checks
    available_db()

    # logic
    r_cmc_query = cmc_query()
    r_parse_cmc_data = parse_cmc_data(r_cmc_query)
    db_insert_data(r_parse_cmc_data)


def main_boilerplate(args: types.SimpleNamespace) -> None:
    """
    init logs, global vars
    """
    global init_args
    init_args = args

    auxiliary.enable_logger(inspect.stack()[1][1], log_to_console=True)
    logging.info(f"{inspect.stack()[1][1] } logging started")
    auxiliary.where_am_i()


def available_db() -> None:
    """
    create a db or use existing
    """
    auxiliary.where_am_i()
    try:
        if os.path.isfile(init_args.db):
            logging.info("db found")
        else:
            logging.info("creating new db")
            engine = sqlalchemy.create_engine(f"sqlite:///{init_args.db}", echo=False)
            with engine.connect() as conn:
                conn.execute(
                    sqlalchemy.text(
                        "CREATE TABLE db ( \
                        symbol TEXT, \
                        name TEXT, \
                        cmc_rank INTEGER, \
                        price REAL, \
                        last_updated TEXT,\
                        percent_change_24h REAL, \
                        percent_change_7d REAL, \
                        percent_change_30d REAL)"
                    )
                )
    except Exception as e:
        logging.error(f"db error: {e}")
        exit()


def cmc_query() -> List[dict]:
    """
    query cmc for data
    """
    auxiliary.where_am_i()
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
    try:
        url = f"{connection_info[mode]['url']}/v1/cryptocurrency/listings/latest?limit={limit}"
        r = requests.get(url, headers=headers)
        response = r.json()["data"]
        return response
    except Exception as e:
        logging.error(f"error getting cmc data: {e}")
        exit()


def parse_cmc_data(cmc_data: List[dict]) -> List[dict]:
    """
    parse and validate data received
    """
    auxiliary.where_am_i()
    parsed_data = []
    for i in cmc_data:
        try:

            if not isinstance(i["quote"]["USD"]["price"], (int, float)):
                logging.error(f"bad price when fetching data: {i}")
                continue

            i_parsed = {
                "name": i["name"],
                "symbol": i["symbol"],
                "price": i["quote"]["USD"]["price"],
                "cmc_rank": i["cmc_rank"],
                "last_updated": i["quote"]["USD"]["last_updated"].split("T")[0],  # leave only date,
                "percent_change_24h": i["quote"]["USD"]["percent_change_24h"],
                "percent_change_7d": i["quote"]["USD"]["percent_change_7d"],
                "percent_change_30d": i["quote"]["USD"]["percent_change_30d"],
            }
            parsed_data.append(i_parsed)

        except Exception as e:
            logging.error(f"error parsing: {e}\n{i}")
            continue

    return parsed_data


def db_insert_data(parsed_cmc_data: List[dict]) -> None:
    """
    add cmc json list to db
    """
    auxiliary.where_am_i()
    if not parsed_cmc_data:
        print("nothing returned by cmc")
        exit(1)

    engine = sqlalchemy.create_engine(f"sqlite:///{init_args.db}", echo=False)
    with engine.connect() as conn:
        for i in parsed_cmc_data:
            conn.execute(
                sqlalchemy.text(
                    "INSERT INTO db (symbol, name, cmc_rank, price, last_updated, percent_change_24h, percent_change_7d, percent_change_30d) \
                    VALUES (:symbol, :name, :cmc_rank, :price, :last_updated, :percent_change_24h, :percent_change_7d, :percent_change_30d)"
                ),
                {
                    "symbol": i["symbol"],
                    "name": i["name"],
                    "cmc_rank": i["cmc_rank"],
                    "price": i["price"],
                    "last_updated": i["last_updated"],
                    "percent_change_24h": i["percent_change_24h"],
                    "percent_change_7d": i["percent_change_7d"],
                    "percent_change_30d": i["percent_change_30d"],
                },
            )
