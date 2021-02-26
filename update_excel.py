import sqlalchemy
import os
import auxiliary
from typing import List
import logging
import types
import datetime
import pandas as pd
import subprocess


"""
get cmc entries from sqlite and store them in excel, optionally mounted via smb
"""

init_args = types.SimpleNamespace()
excel_file = "/mnt/Price DB.xlsx"


def init(args: types.SimpleNamespace) -> None:
    """
    start point
    """

    global init_args
    init_args = args

    auxiliary.enable_logger("update_excel", log_to_console=True)
    logging.info("script started")

    if not db_exists():
        logging.error("db not available")
        exit()
    elif not smb_available():
        logging.error("smb not available")
        exit()

    rows = db_get_data()
    update_excel(rows)


def db_exists() -> bool:
    """
    check if db exists
    """
    if os.path.isfile(init_args.db):
        return True
    else:
        return False


def smb_available() -> bool:
    """
    check and try to mount smb path where excel is
    """
    p = subprocess.run("mount | grep /mnt", shell=True, capture_output=True)
    logging.debug(p)
    if not p.stderr.decode():
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
                return True
            else:
                logging.error(p1.stderr.decode())
                return False
        else:
            logging.info("/mnt already mounted")
            return True
    else:
        logging.error(p.stderr.decode())
        return False


def db_get_data() -> List[sqlalchemy.engine.result.RowProxy]:
    """
    get todays cmc data.
    """
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
    try:
        writer = pd.ExcelWriter(excel_file, engine="xlsxwriter")
        df = pd.DataFrame(rows)
        df.columns = ["symbol", "cmc rank", "price", "name", "last updated"]
        df = df.astype({"cmc rank": int, "price": float})
        df.to_excel(writer, sheet_name="Sheet1", index=False)
        writer.save()
    except Exception as e:
        logging.error(e)
        exit(1)