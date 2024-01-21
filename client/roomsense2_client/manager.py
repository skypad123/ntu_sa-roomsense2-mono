from dataclasses import dataclass
from typing import Optional, Callable
from queue import Queue, Empty
import time
import logging
from threading import Thread, Semaphore
from datetime import datetime, timedelta
from collections import defaultdict
import roomsense2_client.sensors.co2_scd41 as co2_scd41
import roomsense2_client.sensors.humidity_temp_htu2x as htu2x
import roomsense2_client.sensors.light_tsl2591 as tsl2591
import roomsense2_client.services.upload as upload
import asyncio
import board

@dataclass
class AbstractAction:
    expire_datetime: Optional[datetime]
    
## Trigger Actions - marks the start of a new measurement
@dataclass
class SCD41TriggerAction(AbstractAction):
    #CO2 sensor
    pass

@dataclass
class HTU2XTriggerAction(AbstractAction):
    #Humidity and Temperature
    pass

@dataclass
class TSL2591TriggerAction(AbstractAction):
    #Light sensor
    pass

@dataclass
class RPICAMTriggerAction(AbstractAction):
    #Image Camera
    pass

@dataclass
class RPIMICTriggerAction(AbstractAction):
    #Audio Recording
    pass

@dataclass
class HCSRC5031TriggerAction(AbstractAction):
    #Motion sensor
    pass

## I2CReturnAction - marks return data from the I2C bus
@dataclass
class SCD41ReturnAction(AbstractAction):
    #CO2 sensor
    co2: float
    temperature: float
    humidity: float
    reading_time: datetime

@dataclass
class HTU2XReturnAction(AbstractAction):
    #Humidity and Temperature
    temperature: float
    humidity: float
    reading_time: datetime

@dataclass
class TSL2591ReturnAction(AbstractAction):
    #Light sensor
    lux: float
    reading_time: datetime

@dataclass
class RPICAMReturnAction(AbstractAction):
    #Image Camera
    image_location: str
    reading_time: datetime

@dataclass
class RPIMICReturnAction(AbstractAction):
    #Audio Recording
    recording_location: str
    reading_time: datetime

@dataclass
class RPICAMAssetUploadReloadAction(AbstractAction):
    #Image Camera
    bucket_location: str
    reading_time: datetime

@dataclass
class RPIMICAssetUploadReloadAction(AbstractAction):
    #Audio Recording
    bucket_location: str
    reading_time: datetime

@dataclass
class HCSRC5031ReturnAction(AbstractAction):
    #Motion sensor
    motion: bool
    reading_time: datetime


@dataclass
class ActionManagerConfig:
    backend_url: str
    device_name: str


class ActionManager(Thread):

    def __init__(self, config:ActionManagerConfig, *args, **kwargs):
        super(ActionManager, self).__init__(*args, **kwargs)
        self.config = config
        self.action_queue = Queue()
        self.I2CController = I2CController()
        self.RpiCameraController = RpiCameraController()
        self.RpiMicController = RpiMicController()
        self.MotionSensorController = MotionSensorController()

        #state
        self.motion_state = False
        
    def add_action(self, Action):
        self.action_queue.put(Action, block=True, timeout=1)

    def run(self):
        while True: 
            try: 
                # print("ActionManager: checking for new actions")
                Action = self.action_queue.get(block=True, timeout=1)
                if Action is None: 
                    raise Exception("ActionManager: action is None")
                elif(datetime.now() < Action.expire_datetime):
                    logging.debug(f"action popped from queue: {Action}")
                    self.process_actions(Action)
            except Exception as error:
                logging.warning(f"{error}")
                # print("ActionManager: no actions in queue, sleeping for 1 second")
                time.sleep(0.002)
                
    def process_actions(self,action):
        logging.info(f"ActionManager: processing action {action}")
        action_type = type(action).__name__
        action_handlers = {
            'SCD41TriggerAction': self.process_sdc41_trigger_action,
            'HTU2XTriggerAction': self.process_htu2x_trigger_action,
            'TSL2591TriggerAction': self.process_tsl2591_trigger_action,
            'RPICAMTriggerAction': self.process_rpicam_trigger_action,
            'RPIMICTriggerAction': self.process_rpimic_trigger_action,
            'HCSRC5031TriggerAction': self.process_hcsrc5031_trigger_action,
            'SCD41ReturnAction': self.process_sdc41_return_action,
            'HTU2XReturnAction': self.process_htu2x_return_action,
            'TSL2591ReturnAction': self.process_tsl2591_return_action,
            'RPICAMReturnAction': self.process_rpicam_return_action,
            'RPIMICReturnAction': self.process_rpimic_return_action,
            'HCSRC5031ReturnAction': self.process_hcsrc5031_return_action,
            'RPICAMAssetUploadReloadAction': self.process_rpicam_asset_upload_reload_action,
            'RPIMICAssetUploadReloadAction': self.process_rpimic_asset_upload_reload_action
        }
        if action_type in action_handlers:
            action_handlers[action_type](action)

    def process_sdc41_trigger_action(self,Action):
        def callback(ret : co2_scd41.SCD41Reading):
            logging.debug(f"callback triggered with co2_reading: {ret.co2}, temp_reading: {ret.temperature}, humidity_reading: {ret.humidity}")
            self.add_action(SCD41ReturnAction(expire_datetime=Action.expire_datetime, co2 = ret.co2, temperature=ret.temperature, humidity=ret.humidity, reading_time=datetime.now()))
        Thread(target = asyncio.run , args=(self.I2CController.read_sdc41(callback),)).start()

    def process_htu2x_trigger_action(self,Action):
        def callback(ret: htu2x.HTU21DReading):
            logging.debug(f"callback triggered with temp_reading: {ret.temperature}, humidity_reading: {ret.humidity}")
            self.add_action(HTU2XReturnAction(expire_datetime=Action.expire_datetime, temperature = ret.temperature, humidity = ret.humidity, reading_time=datetime.now()))
        Thread(target = asyncio.run , args=(self.I2CController.read_htu2x(callback),)).start()
        
    def process_tsl2591_trigger_action(self,Action):
        def callback(ret: tsl2591.TSL2591Reading):
            logging.debug(f"callback triggered with lux_reading: {ret.lux_reading}")
            self.add_action(TSL2591ReturnAction(expire_datetime=Action.expire_datetime, lux = ret.lux_reading, reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.I2CController.read_tsl2591(callback),)).start()
    
    def process_rpicam_trigger_action(self,Action):
        def callback(image):
            logging.debug(f"callback triggered with image: {image}")
            self.add_action(RPICAMReturnAction(expire_datetime=Action.expire_datetime, image_location = "temp/image.jpg", reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.RpiCameraController.take_picture(callback),)).start()

    def process_rpimic_trigger_action(self,Action):
        def callback(recording):
            logging.debug(f"callback triggered with recording: {recording}")
            self.add_action(RPIMICReturnAction(expire_datetime=Action.expire_datetime, recording_location = "temp/audio.wav" , reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.RpiMicController.take_recording(callback),)).start()

    def process_hcsrc5031_trigger_action(self,Action):
        def callback(ret: bool):
            logging.debug(f"callback triggered with motion: {ret}")
            self.add_action(HCSRC5031ReturnAction(expire_datetime=Action.expire_datetime, motion = ret, reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.MotionSensorController.read_motion(callback),)).start()

    def process_sdc41_return_action(self,action: SCD41ReturnAction):
        #insert spawn new thread to send data to server
        async def upload_sdc41_data():
            backend_url = self.config.backend_url
            device_name = self.config.device_name
            sensor_name = "SCD41"
            timestamp = action.reading_time
            data = upload.Co2HumidityTemperature(co2=action.co2, humidity=action.humidity, temperature=action.temperature)
            logging.info(f"uploading sdc41 data : {action}")
            upload.insert_timeseries(backend_url, timestamp, device_name, sensor_name, data)

        Thread(target= asyncio.run, args=(upload_sdc41_data(),)).start()

    def process_htu2x_return_action(self,action: HTU2XReturnAction):
        #insert spawn new thread to send data to server
        async def upload_htu2x_data():
            backend_url = self.config.backend_url
            device_name = self.config.device_name
            sensor_name = "HTU2X"
            timestamp = action.reading_time
            data = upload.HumidityTemperature(humidity=action.humidity, temperature=action.temperature)
            logging.info(f"uploading htu2x data : {action}")
            upload.insert_timeseries(backend_url, timestamp, device_name, sensor_name, data)

        Thread(target= asyncio.run, args = (upload_htu2x_data(),)).start()

    def process_tsl2591_return_action(self,action: TSL2591ReturnAction):
        #insert spawn new thread to send data to server
        async def upload_tsl2591_data():
            backend_url = self.config.backend_url
            device_name = self.config.device_name
            sensor_name = "TSL2591"
            timestamp = action.reading_time
            data = upload.Brightness(brightness=action.lux)
            logging.info(f"uploading tsl2591 data : {action}")
            upload.insert_timeseries(backend_url, timestamp, device_name, sensor_name, data)

        Thread( target= asyncio.run, args =(upload_tsl2591_data(),)).start()

    #TODO: test returned link
    def process_rpicam_return_action(self,action: RPICAMReturnAction):
        #insert spawn new thread to send data to server
        async def upload_image():
            backend_url = self.config.backend_url
            logging.info(f"uploading image")
            ret = await upload.upload_image(backend_url)
            ### get link fromt ret
            link = ret.result.link
            if link is not None:
                self.add_action(RPICAMAssetUploadReloadAction(expire_datetime=action.expire_datetime, bucket_location = link, reading_time=datetime.now()))
            
        Thread(target= asyncio.run, args =(upload_image(),)).start()

    #TODO: test returned link
    def process_rpimic_return_action(self,action):
        #insert spawn new thread to send data to server
        async def upload_audio():
            backend_url = self.config.backend_url
            logging.info(f"uploading audio")
            ret = await upload.upload_audio(backend_url)
            ### get link fromt ret
            link = ret.result.link
            if link is not None:
                self.add_action(RPIMICAssetUploadReloadAction(expire_datetime=action.expire_datetime, bucket_location = link, reading_time=datetime.now()))

        Thread(target= asyncio.run, args =(upload_audio(),)).start()

    def process_hcsrc5031_return_action(self,action: HCSRC5031ReturnAction):
        #insert spawn new thread to send data to server
        async def trigger_image_capture():
            if  action.motion == True and self.motion_state == False:
                logging.info(f"motion detected, tirggering recording")
                self.motion_state = True
                self.add_action(RPICAMTriggerAction(expire_datetime=datetime.now() + timedelta(seconds=60))) 
            elif action.motion == False:
                self.motion_state = False

        Thread(target= asyncio.run, args =(trigger_image_capture(),)).start()

    def process_rpicam_asset_upload_reload_action(self,action: RPICAMAssetUploadReloadAction):
        #insert spawn new thread to send data to server
        async def upload_rpicam_asset_as_timeseries():
            backend_url = self.config.backend_url
            device_name = self.config.device_name
            sensor_name = "IMAGE"
            timestamp = action.reading_time
            data = upload.Image(image_location=action.bucket_location)
            logging.info(f"uploading rpicam asset as timeseries : {action}")
            upload.insert_timeseries(backend_url, timestamp, device_name, sensor_name, data)

        Thread(target= asyncio.run, args =(upload_rpicam_asset_as_timeseries(),)).start()

    def process_rpimic_asset_upload_reload_action(self,action: RPIMICAssetUploadReloadAction):
        #insert spawn new thread to send data to server
        async def upload_rpimic_asset_as_timeseries():
            backend_url = self.config.backend_url
            device_name = self.config.device_name
            sensor_name = "AUDIO"
            timestamp = action.reading_time
            data = upload.Audio(audio_location=action.bucket_location)
            logging.info(f"uploading rpimic asset as timeseries : {action}")
            upload.insert_timeseries(backend_url, timestamp, device_name, sensor_name, data)

        Thread(target= asyncio.run, args =(upload_rpimic_asset_as_timeseries(),)).start()


## Timing Controller - produces trigger action for acction manager
class TimingController(Thread):

    ref_dict = {
        "SCD41TriggerAction" : SCD41TriggerAction,
        "HTU2XTriggerAction" : HTU2XTriggerAction,
        "TSL2591TriggerAction" : TSL2591TriggerAction,
        "RPICAMTriggerAction" : RPICAMTriggerAction,
        "RPIMICTriggerAction" : RPIMICTriggerAction,
        "HCSRC5031TriggerAction" : HCSRC5031TriggerAction
    }

    managed_actions = {
        "SCD41TriggerAction" : {
            "trigger_interval_s" : 5,
            "trigger_expiration_s" : 60
        },
        "HTU2XTriggerAction" : {
            "trigger_interval_s" : 5,
            "trigger_expiration_s" : 60
        },
        "TSL2591TriggerAction" : {
            "trigger_interval_s" : 5,
            "trigger_expiration_s" : 60
        },
        "RPICAMTriggerAction" : {
            "trigger_interval_s" : 60,
            "trigger_expiration_s" : 60
        },
        "RPIMICTriggerAction" : {
            "trigger_interval_s" : 60,
            "trigger_expiration_s" : 60
        },
        "HCSRC5031TriggerAction" : {
            "trigger_interval_s" : 1,
            "trigger_expiration_s" : 60
        }
    }

    exluded_actions = [
        "SCD41TriggerAction",
        "HTU2XTriggerAction",
        "TSL2591TriggerAction",
        # "RPICAMTriggerAction",
        "RPIMICTriggerAction",
        "HCSRC5031TriggerAction"
    ]

    def __init__(self, *args, **kwargs):
        super(TimingController, self).__init__(*args, **kwargs)
        self.last_trigger_time = defaultdict(lambda: None)
        self.ActionManager = None

    def attach(self,action_manager: ActionManager):
        self.ActionManager = action_manager

    def detach(self):
        self.ActionManager = None

    def is_attached(self):
        return self.ActionManager is not None
    
    def validate_attached(self):
        if not self.is_attached():
            raise Exception("TimingController is not attached to an ActionManager")

    def check_for_trigger(self, action):

        def trigger_action(): 
            logging.debug(f"creating `{action}`")
            expiration_datetime = datetime.now() + timedelta(seconds=self.managed_actions[action]["trigger_expiration_s"])
            action_type = self.ref_dict[action](expiration_datetime)
            self.ActionManager.add_action(action_type)
            self.last_trigger_time[action] = datetime.now() 

        self.validate_attached()
        if self.last_trigger_time[action] is None:
            trigger_action()
        elif datetime.now() > self.last_trigger_time[action] + timedelta(seconds=self.managed_actions[action]["trigger_interval_s"]):
            trigger_action()


    def run(self):
        trigger_list = [ i for i in self.managed_actions if i not in self.exluded_actions]

        while(1):
            for action_type in trigger_list:
                self.check_for_trigger(action_type)

## Resource Controllers
class I2CController:
    def __init__(self):
        self.I2C_bus_access = Semaphore(1)
        self.I2C_bus = board.I2C()
    
    async def read_sdc41(self, callback: Callable[[co2_scd41.SCD41Reading],None]):
        try:
            self.I2C_bus_access.acquire()
            logging.debug("semaphore control: sdc41 acquired bus")
            ret = await co2_scd41.read_scd41(self.I2C_bus)
            callback(ret)
        finally:
            self.I2C_bus_access.release()
            logging.debug("semaphore control: released bus")

    async def read_htu2x(self,callback: Callable[[htu2x.HTU21DReading],None]):
        try:
            self.I2C_bus_access.acquire()
            logging.debug("semaphore control: htu2x acquired bus")
            ret = await htu2x.read_htu2x(self.I2C_bus)
            callback(ret)
        finally:
            self.I2C_bus_access.release()
            logging.debug("semaphore control: htu2x released bus")
        
    async def read_tsl2591(self,callback: Callable[[tsl2591.TSL2591Reading],None]):
        try:
            self.I2C_bus_access.acquire()
            logging.debug("semaphore control:tsl2591 acquired bus")
            ret = await tsl2591.read_tsl2591(self.I2C_bus)
            callback(ret)
        finally:
            self.I2C_bus_access.release()
            logging.debug("semaphore control:tsl2591 released bus")

class RpiCameraController:
    def __init__(self):
        self.rpi_camera_access = Semaphore(1)

    async def take_picture(self,callback: Callable[[None],None]):
        try:
            self.rpi_camera_access.acquire()
            logging.debug("semaphore control: rpi camera acquired")
            # insert rpi camera capture logic here
            callback()
        finally:
            self.rpi_camera_access.release()
            logging.debug("semaphore control: rpi camera released")

class RpiMicController:
    def __init__(self):
        self.rpi_mic_access = Semaphore(1)

    async def take_recording(self,callback: Callable[[None],None]):
        try:
            self.rpi_mic_access.acquire()
            logging.debug("semaphore control: rpi mic acquired")
            # insert rpi camera capture logic here
            callback()
        finally:
            self.rpi_mic_access.release()
            logging.debug("semaphore control: rpi mic released")

class MotionSensorController:
    def __init__(self):
        self.motion_sensor_access = Semaphore(1)

    async def read_motion(self, callback: Callable[[bool],None]):
        try:
            self.motion_sensor_access.acquire()
            logging.debug("semaphore control: motion sensor acquired")
            # insert motion sensor reading logic here
            callback(True)
        finally:
            self.motion_sensor_access.release()
            logging.debug("semaphore control: motion sensor released")

## dummy async function for testing
async def dummy_async_fn(proces_name: str):
    # time.sleep(0.002)
    await asyncio.sleep(0.002)
    return