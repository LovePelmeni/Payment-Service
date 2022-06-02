import logging
logger = logging.getLogger(__name__)
formatter = logging.Formatter()
handler = logging.FileHandler(filename='payment_log', mode='w')

handler.setFormatter(formatter)
handler.setLevel(level='DEBUG')
logger.addHandler(handler)

