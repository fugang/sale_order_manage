import yaml
import logging
from logging.handlers import RotatingFileHandler

gw = {}
config_doc = open("config.yaml", "r")
config = yaml.load(config_doc, Loader=yaml.FullLoader)

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        RotatingFileHandler("platform.log",
                                            maxBytes=2 * 1000 * 1000,
                                            backupCount=5)
                    ])
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
