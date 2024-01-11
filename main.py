import logging
import loginMenu
from datetime import datetime

if __name__ == "__main__":
    start_time = datetime.now()
    logFile = f'Logs/Voucher_Export_{start_time.year}-{start_time.month}-{start_time.day}--{start_time.hour}-{start_time.minute}-{start_time.second}.log'
    logging.basicConfig(filename=logFile, encoding='utf-8', level=logging.DEBUG,
                    format='%(asctime)s | %(levelname)s | %(message)s', datefmt='%m/%d/%Y %H:%M:%S')
    logging.info("Beginning Log")

    config_name = "config - dryrun.json"

    logging.info(f"Configured with config_name = {config_name}")
    try:
        loginMenu.loginMenu(config_name)
    except Exception as e:
        logging.exception(e)
        raise e