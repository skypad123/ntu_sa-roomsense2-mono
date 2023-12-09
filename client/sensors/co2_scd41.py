# from smbus2 import SMBus
# import time

# class SDC41:
#     def __init__(self):
#         pass
#             # with SMBus(1) as bus:
#             #     print("starting periodic measurement")
#             #     bus.write_i2c_block_data(0x62, 0x21,[0xB1])
#             #     time.sleep(0.010)
        
#     def read_co2():
#         with SMBus(1) as bus:
#         # try:
#             print("starting measurement loop")
#             while 1: 
#                 # b = bus.read_i2c_block_data(0x62, 0, 16)

#                 bus.write_i2c_block_data(0x62, 0xE4,[0xB8]) #get_data_ready_status
#                 time.sleep(0.01)
#                 b = bus.read_i2c_block_data(0x62, 0, 3)
#                 time.sleep(0.01)
#                 print(b)
#                 if (b[0] & 0b011111111111) == 0x00:
#                     print("no data ready")
#                     time.sleep(0.1)
#                     continue
#                 else:
#                     print("data ready")
#                     bus.write_i2c_block_data(0x62, 0xEC, [0x05])
#                     time.sleep(0.2)
#                     b = bus.read_i2c_block_data(0x62, 0x00, 9)
#                     print(b)
#                     time.sleep(1)

#     def __exit__(self, exc_type, exc_value, traceback):
#         with SMBus(1) as bus:
#             print("stopping periodic measurement")
#             bus.write_i2c_block_data(0x62, 0x3f, [0x86])
#             time.sleep(0.500)
#             print("periodic measurement stopped")

# if __name__ == "__main__":
#     # with SDC41() as sdc41:
#     #     sdc41.read_co2()
#     with SMBus(1) as bus:
#         print("starting measurement loop")
#         while 1: 
#             # b = bus.read_i2c_block_data(0x62, 0, 16)

#             bus.write_i2c_block_data(0x62, 0xE4,[0xB8]) #get_data_ready_status
#             time.sleep(0.01)
#             b = bus.read_i2c_block_data(0x62, 0, 3)
#             time.sleep(0.01)
#             print(b)
#             if (b[0] & 0b011111111111) == 0x00:
#                 print("no data ready")
#                 time.sleep(1)
#                 continue
#             else:
#                 try:
#                     print("data ready")
#                     bus.write_i2c_block_data(0x62, 0xEC, [0x05])
#                     print("requesting measurement")
#                     time.sleep(0.01)
#                     b = bus.read_i2c_block_data(0x62, 0x00, 9)
#                     print(f"recieved measurement:{b}")
#                     time.sleep(5)
#                 except Exception as e:
#                     print(e)
#                     time.sleep(1)
#                     continue


#SDC measurement window is 5 seconds



import time
import board
from adafruit_scd4x import SCD4X

i2c = board.I2C()
scd4x = SCD4X(i2c)
print("Serial number:", [hex(i) for i in scd4x.serial_number])

scd4x.start_periodic_measurement()
print("Waiting for first measurement....")

while True:
    if scd4x.data_ready:
        print("CO2: %d ppm" % scd4x.CO2)
        print("Temperature: %0.1f *C" % scd4x.temperature)
        print("Humidity: %0.1f %%" % scd4x.relative_humidity)
        print()
    time.sleep(1)