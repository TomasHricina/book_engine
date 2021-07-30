def create_logger(app_name):
    import logging
    import os
    """Create a logging interface"""
    logging_level = os.getenv('logging', logging.INFO)
    logging.basicConfig(
        level=logging_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(app_name)
    return logger
