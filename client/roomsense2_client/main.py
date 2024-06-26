from roomsense2_client.manager import ActionManager , TimingController, ActionManagerConfig
from roomsense2_client.services.upload import insert_device
from threading import Thread
import asyncio
import logging
import sys
from dotenv import load_dotenv, dotenv_values

class CustomFormatter(logging.Formatter):

    grey = "\x1b[38;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: grey + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
    

root = logging.getLogger()
root.setLevel(logging.DEBUG)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(CustomFormatter())
root.addHandler(handler)

load_dotenv()
config = dotenv_values(".env")
backend_url = config["API_ENDPOINT"]
device_name = config["DEVICE_NAME"]

logging.debug(f"Backend URL: {backend_url}")

asyncio.run(insert_device(backend_url))

action_config = ActionManagerConfig(backend_url, device_name)

action_manager = ActionManager(action_config)
timing_controller = TimingController()
timing_controller.attach(action_manager)
timing_controller.start()
action_manager.start()
timing_controller.join()
action_manager.join()

    
