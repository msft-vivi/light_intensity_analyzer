import logging
from argparse import ArgumentParser
from .config import Config

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s')
ENABLE_LOGGING = True

def log(message : str):
    if ENABLE_LOGGING:
        logging.info(message)

def parse_args_to_config(args, config : Config):
    if hasattr(args, 'color'):
        config.target_color = args.color
    
