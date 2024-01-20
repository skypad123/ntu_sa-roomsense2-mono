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
import asyncio

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
    image: bytes
    reading_time: datetime

@dataclass
class RPIMICReturnAction(AbstractAction):
    #Image Camera
    recording: bytes
    reading_time: datetime

@dataclass
class HCSRC5031ReturnAction(AbstractAction):
    #Motion sensor
    motion: bool
    reading_time: datetime


class ActionManager(Thread):

    def __init__(self, *args, **kwargs):
        super(ActionManager, self).__init__(*args, **kwargs)
        self.action_queue = Queue()
        self.I2CController = I2CController()
        self.RpiCameraController = RpiCameraController()
        self.RpiMicController = RpiMicController()
        self.MotionSensorController = MotionSensorController()
        
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
            'HCSRC5031ReturnAction': self.process_hcsrc5031_return_action
        }
        if action_type in action_handlers:
            action_handlers[action_type](action)

    def process_sdc41_trigger_action(self,Action):
        def callback(co2_reading):
            logging.debug(f"callback triggered with co2_reading: {co2_reading}")
            self.add_action(SCD41ReturnAction(expire_datetime=Action.expire_datetime, co2 = co2_reading, reading_time=datetime.now()))
        Thread(target = asyncio.run , args=(self.I2CController.read_sdc41(callback),)).start()

    def process_htu2x_trigger_action(self,Action):
        def callback(temp_reading, humidity_reading):
            logging.debug(f"callback triggered with temp_reading: {temp_reading}, humidity_reading: {humidity_reading}")
            self.add_action(HTU2XReturnAction(expire_datetime=Action.expire_datetime, temperature = temp_reading, humidity = humidity_reading, reading_time=datetime.now()))
        Thread(target = asyncio.run , args=(self.I2CController.read_htu2x(callback),)).start()
        
    def process_tsl2591_trigger_action(self,Action):
        def callback(lux_reading):
            logging.debug(f"callback triggered with lux_reading: {lux_reading}")
            self.add_action(TSL2591ReturnAction(expire_datetime=Action.expire_datetime, lux = lux_reading, reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.I2CController.read_tsl2591(callback),)).start()
    
    def process_rpicam_trigger_action(self,Action):
        def callback(image):
            logging.debug(f"callback triggered with image: {image}")
            self.add_action(RPICAMReturnAction(expire_datetime=Action.expire_datetime, image = image, reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.RpiCameraController.take_picture(callback),)).start()

    def process_rpimic_trigger_action(self,Action):
        def callback(recording):
            logging.debug(f"callback triggered with recording: {recording}")
            self.add_action(RPIMICReturnAction(expire_datetime=Action.expire_datetime, recording=recording , reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.RpiMicController.take_recording(callback),)).start()

    def process_hcsrc5031_trigger_action(self,Action):
        def callback(motion_reading):
            logging.debug(f"callback triggered with motion: {motion_reading}")
            self.add_action(HCSRC5031ReturnAction(expire_datetime=Action.expire_datetime, motion = motion_reading, reading_time=datetime.now()))
        Thread(target = asyncio.run, args=(self.MotionSensorController.read_motion(callback),)).start()

    #TODO: implement server communication
    def process_sdc41_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_sdc41():
            logging.info(f"returning co2 : {Action.co2}")
        Thread(target= asyncio.run, args=(print_sdc41(),)).start()

    #TODO: implement server communication
    def process_htu2x_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_htu2x():
            logging.info(f"returning temp : {Action.temperature}, humidity : {Action.humidity}")
        Thread(target= asyncio.run, args = (print_htu2x(),)).start()

    #TODO: implement server communication
    def process_tsl2591_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_tsl2591():
            logging.info(f"returning lux : {Action.lux}")
        Thread( target= asyncio.run, args =(print_tsl2591(),)).start()

    #TODO: implement server communication
    def process_rpicam_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_rpicam():
            logging.info(f"returning image : {Action.image}")
        Thread(target= asyncio.run, args =(print_rpicam(),)).start()

    #TODO: implement server communication
    def process_rpimic_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_rpimic():
            logging.info(f"returning recording : {Action.recording}")
        Thread(target= asyncio.run, args =(print_rpimic(),)).start()

    #TODO: implement server communication
    def process_hcsrc5031_return_action(self,Action):
        #insert spawn new thread to send data to server
        async def print_hcsrc5031():
            logging.info(f"returning motion : {Action.motion}")
        Thread(target= asyncio.run, args =(print_hcsrc5031(),)).start()

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
        while(1):
            for action_type in self.managed_actions:
                self.check_for_trigger(action_type)

## Resource Controllers
class I2CController:
    def __init__(self):
        self.I2C_bus_access = Semaphore(1)
        # self.I2C_bus = board.I2C()
    
    async def read_sdc41(self, callback: Callable[[float],None]):
        try:
            self.I2C_bus_access.acquire()
            logging.debug("semaphore control: sdc41 acquired bus")
            # ret = await co2_scd41.read_scd41(self.I2C_bus)
            await dummy_async_fn("read_sdc41")
            ret = co2_scd41.SCD41Reading(co2=0,temperature=0,humidity=0)
            callback(ret.co2)
        finally:
            self.I2C_bus_access.release()
            logging.debug("semaphore control: released bus")


    async def read_htu2x(self,callback: Callable[[float,float],None]):
        try:
            self.I2C_bus_access.acquire()
            logging.debug("semaphore control: htu2x acquired bus")
            # ret = await htu2x.read_htu2x(self.I2C_bus)
            # ret = htu2x.HTU2XReading(temperature=0,humidity=0)
            await dummy_async_fn("read_htu2x")
            ret = htu2x.HTU21DReading(temperature=0,humidity=0)
            callback(ret.temperature,ret.humidity)
        finally:
            self.I2C_bus_access.release()
            logging.debug("semaphore control: htu2x released bus")
        

    async def read_tsl2591(self,callback: Callable[[float],None]):
        try:
            self.I2C_bus_access.acquire()
            logging.debug("semaphore control:tsl2591 acquired bus")
            # ret = await tsl2591.read_tsl2591(self.I2C_bus)
            await dummy_async_fn("read_tsl2591")
            ret = tsl2591.TSL2591Reading(lux_reading=0,infrared=0,visible=0,full_spectrum=0)
            callback(ret.lux_reading)
        finally:
            self.I2C_bus_access.release()
            logging.debug("semaphore control:tsl2591 released bus")

class RpiCameraController:
    def __init__(self):
        self.rpi_camera_access = Semaphore(1)

    async def take_picture(self,callback: Callable[[bytes],None]):
        try:
            self.rpi_camera_access.acquire()
            logging.debug("semaphore control: rpi camera acquired")
            # insert rpi camera capture logic here
            callback(bytes([0]))
        finally:
            self.rpi_camera_access.release()
            logging.debug("semaphore control: rpi camera released")

class RpiMicController:
    def __init__(self):
        self.rpi_mic_access = Semaphore(1)

    async def take_recording(self,callback: Callable[[bytes],None]):
        try:
            self.rpi_mic_access.acquire()
            logging.debug("semaphore control: rpi mic acquired")
            # insert rpi camera capture logic here
            callback(bytes([0]))
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