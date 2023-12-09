from dataclasses import dataclass
from typing import Optional, Callable
from queue import Queue, Empty
import time
import logging
from threading import Thread, Semaphore
from datetime import datetime, timedelta
from collections import defaultdict
import board
import sensors.co2_scd41 as co2_scd41
import sensors.humidity_temp_htu2x as htu2x
import sensors.light_tsl2591 as tsl2591

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
class HCSRC5031TriggerAction(AbstractAction):
    #Motion sensor
    pass

@dataclass
class RPICAMTriggerAction(AbstractAction):
    #Image Camera
    pass

@dataclass
class SGM58031TriggerAction(AbstractAction):
    #Audio Mic
    pass

## I2CReturnAction - marks return data from the I2C bus
@dataclass
class SCD41ReturnAction(AbstractAction):
    #CO2 sensor
    co2: float
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
class HCSRC5031ReturnAction(AbstractAction):
    #Motion sensor
    motion: bool
    reading_time: datetime

@dataclass
class RPICAMReturnAction(AbstractAction):
    #Image Camera
    image: bytes
    reading_time: datetime

@dataclass
class SGM58031ReturnAction(AbstractAction):
    #Audio Mic
    audio: list[float]
    reading_time: datetime


## Config
@dataclass
class AudioClipConfig: 
    reading_interval_ms: int 
    reading_duration_ms: int

class ActionManager:
    def __init__(self):
        self.action_queue = Queue()
        self.I2CController = I2CController()
        self.RpiCameraController = RpiCameraController()
        self.MotionSensorController = MotionSensorController()
        
    def add_action(self, Action):
        self.Action_queue.put(Action)

    async def run(self):
        while True: 
            try: 
                logging.info("ActionManager: checking for new actions")
                Action = self.Action_queue.get_nowait()
                if (datetime.now() < Action.expire_datetime):
                    self.process_action(Action)
            except Empty:
                logging.info("ActionManager: no actions in queue, sleeping for 1 second")
                time.sleep(0.001)
                

    async def process_actions(self,action):
        action_type = type(action).__name__
        action_handlers = {
            'SCD41TriggerAction': self.process_sdc41_trigger_action,
            'HTU2XTriggerAction': self.process_htu2x_trigger_action,
            'TSL2591TriggerAction': self.process_tsl2591_trigger_action,
            'SGM58031TriggerAction': self.process_sgm58031_trigger_action,
            'RPICAMTriggerAction': self.process_rpicam_trigger_action,
            'HCSRC5031TriggerAction': self.process_hcsrc5031_trigger_action
        }
        if action_type in action_handlers:
            await action_handlers[action_type](action)

    async def process_sdc41_trigger_action(self,Action):
        async def callback(co2_reading):
            self.add_action(SCD41ReturnAction(co2 = co2_reading, reading_time=datetime.now()))
        Thread(target = self.I2CController.read_sdc41, args=(callback,)).start()

    async def process_htu2x_trigger_action(self,Action):
        async def callback(temp_reading, humidity_reading):
            self.add_action(HTU2XReturnAction(temperature = temp_reading, humidity = humidity_reading, reading_time=datetime.now()))
        Thread(target = self.I2CController.read_htu2x, args=(callback,)).start()
        
    async def process_tsl2591_trigger_action(self,Action):
        async def callback(lux_reading):
            self.add_action(TSL2591ReturnAction(lux = lux_reading, reading_time=datetime.now()))
        Thread(target = self.I2CController.read_tsl2591, args=(callback,)).start()
    
    async def process_sgm58031_trigger_action(self,Action):
        async def callback(audio_reading):
            self.add_action(SGM58031ReturnAction(audio = audio_reading, reading_time=datetime.now()))
        Thread(target = self.I2CController.read_sgm58031, args=(callback,)).start()

    async def process_rpicam_trigger_action(self,Action):
        async def callback(image):
            self.add_action(RPICAMReturnAction(image = image, reading_time=datetime.now()))
        Thread(target = self.RpiCameraController.take_picture, args=(callback,)).start()

    async def process_hcsrc5031_trigger_action(self,Action):
        async def callback(motion_reading):
            self.add_action(SCD41ReturnAction(motion = motion_reading, reading_time=datetime.now()))
        Thread(target = self.MotionSensorController.read_motion, args=(callback,)).start()

    async def process_sdc41_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_sdc41():
            print(f"co2 : {Action.co2}")
        runnable = Thread(target = print_sdc41)
        runnable.start()

    async def process_htu2x_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_htu2x():
            print(f"temp : {Action.temperature}, humidity : {Action.humidity}")
        runnable = Thread(target = print_htu2x)
        runnable.start()


    async def process_tsl2591_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_tsl2591():
            print(f"lux : {Action.lux}")
        runnable = Thread(target = print_tsl2591 )
        runnable.start()

    async def process_sgm58031_return_action(self,Action):
        #insert spawn new thread to send data to server
        pass

    async def process_rpicam_return_action(self,Action):
        #insert spawn new thread to send data to server
        pass

    async def process_hcsrc5031_return_action(self,Action):
        #insert spawn new thread to send data to server
        pass





## Timing Controller - produces trigger action for acction manager
class TimingController:

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
        # "SGM58031TriggerAction" : {
        #     "trigger_interval_s" : 5,
        #     "trigger_expiration_s" : 60
        # },
        "RPICAMTriggerAction" : {
            "trigger_interval_s" : 5,
            "trigger_expiration_s" : 60
        },
        "HCSRC5031TriggerAction" : {
            "trigger_interval_s" : 5,
            "trigger_expiration_s" : 60
        }
    }

    def __init__(self):
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
        self.validate_attached()
        action_type = type(action).__name__
        is_none = self.last_trigger_time[action_type] is None
        need_trigger = datetime.now() > self.last_trigger_time[action_type] + timedelta(seconds=self.managed_actions[action_type]["trigger_interval_s"])
        if is_none or need_trigger:
            self.ActionManager.add_action(action)
            self.last_trigger_time[action_type] = datetime.now()

    def run(self):
        while(1):
            for action_type in self.managed_actions:
                self.check_for_trigger(action_type)

## Resource Controllers
class I2CController:
    def __init__(self):
        self.I2C_bus_access = Semaphore(1)
        self.I2C_bus = board.I2C()
    
    async def read_sdc41(self, callback: Callable[[float],None]):
        try:
            self.I2C_bus_access.acquire()
            ret = await co2_scd41.read_scd41(self.I2C_bus)
            callback(ret.co2)
        finally:
            self.I2C_bus_access.release()


    async def read_htu2x(self,callback: Callable[[float,float],None]):
        try:
            self.I2C_bus_access.acquire()
            ret = await htu2x.read_htu2x(self.I2C_bus)
            callback(ret.temperature,ret.humidity)
        finally:
            self.I2C_bus_access.release()
        

    async def read_tsl2591(self,callback: Callable[[float],None]):
        try:
            self.I2C_bus_access.acquire()
            ret = await tsl2591.read_tsl2591(self.I2C_bus)
            callback(ret.lux_reading)
        finally:
            self.I2C_bus_access.release()

    async def read_sgm58031(self,config:AudioClipConfig,callback: Callable[[list[float]],None]):
        readings = []
        start_time = datetime.now()
        while(datetime.now() < start_time + timedelta(milliseconds=config.reading_duration_ms)):
            try:
                self.I2C_bus_access.acquire()
                # insert audio sensor reading logic here
                readings.append(0)
            finally:
                self.I2C_bus_access.release()
                time.sleep(config.reading_interval_ms/1000)
        if len(readings) > 0:
            callback(readings)

class RpiCameraController:
    def __init__(self):
        self.rpi_camera_access = Semaphore(1)

    async def take_picture(self,callback: Callable[[None],None]):
        self.rpi_camera_access.acquire()
        try:
            # insert rpi camera capture logic here
            callback(None)
        finally:
            self.rpi_camera_access.release()

class MotionSensorController:
    def __init__(self):
        self.motion_sensor_access = Semaphore(1)

    async def read_motion(self, callback: Callable[[bool],None]):
        self.motion_sensor_access.acquire()
        try:
            # insert motion sensor reading logic here
            callback(True)
        finally:
            self.motion_sensor_access.release()
