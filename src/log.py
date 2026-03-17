import logging

def get_logger(log_level=logging.INFO):
    if type(log_level) == str:
        log_level = log_level.upper()
        
    logger = logging.getLogger()
    logger.setLevel(log_level)

    stderr_handler = logging.StreamHandler()
    stderr_handler.setLevel(log_level)

    if logger.level == logging.DEBUG:
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(filename)s: %(funcName)s:%(lineno)d:  %(message)s")
    else:
        formatter = logging.Formatter("%(asctime)s %(levelname)s : %(message)s")
    stderr_handler.setFormatter(formatter)

    logger.addHandler(stderr_handler)

    return logger
