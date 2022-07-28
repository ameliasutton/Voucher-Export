from logger import logger
from configMenu import configMenu
from datetime import datetime

if __name__ == "__main__":
    current_time = datetime.now()
    logger = logger(f"Logs/Voucher_Export_{current_time.year:02}-{current_time.month:02}-{current_time.day:02}_{current_time.hour:02}-"
                    f"{current_time.minute:02}-{current_time.second:02}")
    print("Launching...")
    try:
        configMenu()
    except Exception as e:
        print(f"| Fatal Error | {e}\n")
        raise e

