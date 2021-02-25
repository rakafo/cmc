from sqlalchemy import create_engine, text
import os
import auxiliary
import requests
from typing import List
import json
import logging

args = {}

"""
query cmc and store results in sqlite db.
"""


def init(init_args: dict):
    """
    start point
    """
    global args
    args = init_args

    logging.basicConfig(
        filename="query_and_store.py.log",
        filemode="a+",
        format="%(asctime)s - %(levelname)s - %(message)s",
        level=logging.DEBUG,
    )

    if db_init():
        cmc_data = cmc_query()
        db_insert_data(cmc_data)


def db_init() -> bool:
    """
    create a db or use existing
    """
    if os.path.isfile(args["db"]):
        return True
    else:
        with db_connect().connect() as conn:
            conn.execute(text("CREATE TABLE db (id INTEGER PRIMARY KEY, data JSON)"))
            return True


def db_connect():
    """
    get sqlite object
    """
    engine = create_engine(f"sqlite:///{args['db']}", echo=False)
    return engine


def cmc_query() -> List[dict]:
    """
    query cmc for data
    """
    connection_info = {
        "pro": {
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
        "X-CMC_PRO_API_KEY": connection_info[args["mode"]]["api"],
    }
    url = f"{connection_info[args['mode']]['url']}/v1/cryptocurrency/listings/latest?limit={args['limit']}"
    r = requests.get(url, headers=headers)
    response = r.json()["data"]
    return response


def db_insert_data(cmc_data: List[dict]) -> None:
    """
    add cmc json list to db
    """
    if not cmc_data:
        print("nothing returned by cmc")
        exit(1)

    with db_connect().connect() as conn:
        for i in cmc_data:
            conn.execute(
                text("INSERT INTO db (data) VALUES (:data)"), {"data": json.dumps(i)}
            )
