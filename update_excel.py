import sqlalchemy
import os
import auxiliary
from typing import List
import logging
import types
import datetime
import pandas as pd
import subprocess
import inspect


"""
get cmc entries from sqlite and store them in excel, optionally mounted via smb
"""

init_args = types.SimpleNamespace()
excel_file = "/mnt/Price DB.xlsx"


def main(args: types.SimpleNamespace) -> None:
    """
    start point
    """
    main_boilerplate(args)

    # pre-checks
    available_db()
    available_smb()

    # logic
    rows = db_get_data()
    update_excel(rows)


def main_boilerplate(args: types.SimpleNamespace) -> None:
    """
    init logs, global vars
    """
    global init_args
    init_args = args

    auxiliary.enable_logger(inspect.stack()[1][1], log_to_console=True)
    logging.info(f"{inspect.stack()[1][1]} logging started")
    auxiliary.where_am_i()


def available_db() -> None:
    """
    check if db exists
    """
    auxiliary.where_am_i()
    if not os.path.isfile(init_args.db):
        logging.error("db not available")
        exit()


def available_smb() -> None:
    """
    check and try to mount smb path where excel is
    """
    auxiliary.where_am_i()
    p = subprocess.run("mount | grep /mnt", shell=True, capture_output=True)
    if not p.stderr.decode():  # 0 if found, 1 if not found
        if not p.stdout.decode():
            user = auxiliary.get_conf()["smb"]["user"]
            password = auxiliary.get_conf()["smb"]["pass"]
            p1 = subprocess.run(
                f"mount -t cifs -o username={user},password={password},rw //192.168.122.3/shared /mnt",
                shell=True,
                capture_output=True,
            )
            logging.info(p1)
            if not p1.stderr.decode():
                logging.info("/mnt mounted")
                return
            else:
                logging.error(f"smb not available: {p1.stderr.decode()}")
                exit()
        else:
            logging.info("/mnt already mounted")
            return
    else:
        logging.error(p.stderr.decode())
        exit()


def db_get_data() -> List[sqlalchemy.engine.result.RowProxy]:
    """
    get todays cmc data.
    """
    auxiliary.where_am_i()
    engine = sqlalchemy.create_engine(f"sqlite:///{init_args.db}", echo=False)
    with engine.connect() as conn:
        result = conn.execute(
            sqlalchemy.text(
                "SELECT * \
                FROM db \
                WHERE last_updated = :last_updated"
            ),
            {"last_updated": datetime.datetime.now().date()},
        )
        results = [i for i in result]
        return results


def update_excel(rows: List[sqlalchemy.engine.result.RowProxy]) -> None:
    """
    update excel with sql info.
    """
    auxiliary.where_am_i()
    try:
        writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
        df = pd.DataFrame(rows)
        df.columns = ["symbol", "name", "cmc_rank", "price", "last updated", "percent_change_24h", "percent_change_7d", "percent_change_30d"]
        df = df.astype({"cmc_rank": int, "price": float})
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        writer.save()
    except Exception as e:
        logging.error(e)
        exit()
