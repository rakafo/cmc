import yaml
import logging

__version__ = (1, 0, 0)


def get_conf() -> yaml:
    """
    load yaml config.
    should be used for sensitive information so it's not tracked by git.
    """
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

    file_log_handler = logging.FileHandler(f"{fname}.log")
    file_log_handler.setFormatter(formatter)
    logger.addHandler(file_log_handler)

    if log_to_console:
        stderr_log_handler = logging.StreamHandler()
        stderr_log_handler.setFormatter(formatter)
        logger.addHandler(stderr_log_handler)
