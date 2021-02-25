"""
version: 1.0.0
"""

import yaml


def get_conf() -> yaml:
    with open("conf.yml", "r") as f:
        config = yaml.safe_load(f.read())
        return config
