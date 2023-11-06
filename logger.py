import logging

logger = logging.getLogger("pdfReader")

file_handler = logging.FileHandler(filename="./info.log")
console_handler = logging.StreamHandler()

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(lineno)d - %(message)s')

file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

logger.addHandler(file_handler)

logger.setLevel(level=logging.DEBUG)