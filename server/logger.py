""" 2021 Created by michal@buyuk-dev.com

    Logging configuration.
"""

import logging

logging.basicConfig(format="%(asctime)s %(threadName)s %(levelname)s %(message)s")
logger = logging.getLogger("main")
logger.setLevel(logging.DEBUG)
