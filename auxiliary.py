import yaml
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import inspect
import re

__version__ = (1, 3, 0)


def get_conf() -> yaml:
    """
    load yaml config
    contains sensitive and regular data as dict
    """
    where_am_i()

    with open("conf.yml", "r") as f:
        config = yaml.safe_load(f.read())
        return config


def enable_logger(fname: str, log_to_console: bool = False) -> None:
    """
    enable logging to file and optionally console.
    needs to be done this way instead of basicConfig as it doesn't allow logging to both console and file.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # log to file
    file_log_handler = logging.FileHandler(f"{fname}.log")
    file_log_handler.setFormatter(formatter)
    logger.addHandler(file_log_handler)

    # log to console
    if log_to_console:
        stderr_log_handler = logging.StreamHandler()
        stderr_log_handler.setFormatter(formatter)
        logger.addHandler(stderr_log_handler)


def check_log(fname: str) -> None:
    """
    check log file for specified keywords and send email on trigger
    """
    with open(fname) as log_file:
        logs = log_file.read()

    # get last run
    logs_last_run = re.split("(.+? logging started\n)", logs)[-2:]  # () brackets so searched line is included
    logs_last_run = "".join(logs_last_run)
    if bool(re.search("WARNING|ERROR", logs_last_run)):
        subject = f"{fname} execution log"
        body = re.sub("\n", "<br>", logs_last_run)
        send_email(subject, body)


def where_am_i(debug: bool = True) -> None:
    """
    shows the calling function
    """
    if debug:
        calling_function = inspect.stack()[1][3]
        logging.info(f"In function: {calling_function}()")


def send_email(subject: str, body: str) -> None:
    """
    send a html formatted email.
    displays correctly in thunderbird.
    """
    where_am_i()

    email_from = get_conf()["gmail"]["user"]
    email_pass = get_conf()["gmail"]["pass"]
    email_to = [get_conf()["gmail"]["user"]]

    msg = MIMEMultipart("alternative")
    msg["From"] = email_from
    msg["To"] = ",".join(email_to)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    mail_server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    mail_server.login(email_from, email_pass)
    mail_server.sendmail(email_from, email_to, msg.as_string())
    mail_server.close()
