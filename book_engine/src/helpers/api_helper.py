#!/usr/bin/python3
from book_engine.src.helpers.path_helpers import child_path
import logging


# Allowes logger to work both locally and as imported module
if __name__ == 'main':
    root_package = __package__.split('.')[0]
    logger = logging.getLogger(root_package)
else:
    logger = logging


def get_api_credentials():
    api_key_path = child_path('credentials', 'api_key.txt')
    try:
        with open(api_key_path, 'r') as f:
            api_key = f.readline()
            logger.warning("API key WAS found, trying accessing with API now...")
            return api_key
    except FileNotFoundError:
        logger.warning("API key not found, accessing API without key (lower throughput)...")