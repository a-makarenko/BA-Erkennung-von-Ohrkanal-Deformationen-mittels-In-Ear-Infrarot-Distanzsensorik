# File to read proximity sensor data.
# Sensor: VCNL4020 (http://www.vishay.com/docs/84136/designingvcnl4020.pdf).
# Author: Anastassiya Makarenko.
 
import smbus
import time
import sys
import struct
 
 
# Constants.
 
# VCNL4020 constants:
VCNL4020_BUS_ADDRESS                = 0x13  # Bus Address of VCNL4020.
VCNL4020_REGISTER_COMMAND           = 0x80  # Address of Command Register.
VCNL4020_REGISTER_PROX_RATE         = 0x82  # Address of Proximity Rate Register.
VCNL4020_REGISTER_IR_LED_CURRENT    = 0x83  # Address of Register for LED current Setting.
VCNL4020_REGISTER_PROX_RESULT       = 0x87  # Address of Proximity Measurement Result Register (87h + 88h) (16 bit value).
 
# Constants for Proximity Rate Register:
PROX_MEASUREMENT_RATE_2       = 0x00  #   1.95     proximity measeurements/sec     (DEFAULT)
PROX_MEASUREMENT_RATE_4       = 0x01  #   3.090625 proximity measeurements/sec
PROX_MEASUREMENT_RATE_8       = 0x02  #   7.8125   proximity measeurements/sec
PROX_MEASUREMENT_RATE_16      = 0x03  #   16.625   proximity measeurements/sec
PROX_MEASUREMENT_RATE_31      = 0x04  #   31.25    proximity measeurements/sec
PROX_MEASUREMENT_RATE_62      = 0x05  #   62.5     proximity measeurements/sec
PROX_MEASUREMENT_RATE_125     = 0x06  #   125      proximity measeurements/sec
PROX_MEASUREMENT_RATE_250     = 0x07  #   250      proximity measeurements/sec
 
# Constants for IR LED Current Register:
IR_LED_CURRENT_0  = 0  # IR LED Current = 0 mA
IR_LED_CURRENT_10 = 1  # IR LED Current = 10 mA
IR_LED_CURRENT_20 = 2  # IR LED Current = 20 mA     (DEFAULT)
IR_LED_CURRENT_30 = 3  # IR LED Current = 30 mA
IR_LED_CURRENT_40 = 4  # IR LED Current = 40 mA
 
# Constants.
rate = 1./60
 
# Initialisation.
 
# Get I2C bus.
bus = smbus.SMBus(1)
 
# Set Proximity Rate Register (0x82).
# Settings: 125 Hz.
# Command Register must be all 0 to set prox_rate.
bus.write_byte_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_COMMAND, 0x00)
value = PROX_MEASUREMENT_RATE_125 & 0xFF  # Proximity Rate
bus.write_byte_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_PROX_RATE, value)
prox_rate = bus.read_byte_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_PROX_RATE) & 0xFF
 
# Set IR LED Current REgister (0x83).
# Settings: 40 mA.
c_value = IR_LED_CURRENT_40 & 0xFF
bus.write_byte_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_IR_LED_CURRENT, c_value)
current = bus.read_byte_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_IR_LED_CURRENT)
 
# Set Command Register (0x80).
# Settings: Enabels periodic proximity measurements,
#           Enabels state machine and LP oscillator for selftimed measurement.
com_value = 0x02
com_value = com_value & 0xFF
bus.write_byte_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_COMMAND, com_value)
com_value = 0x03
com_value = com_value & 0xFF
bus.write_byte_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_COMMAND, com_value)
 
 
def getProximity():
     
    # Read data back from Proximity Result Registers (0x87 and  0x88), 2 bytes.
    data = bus.read_i2c_block_data(VCNL4020_BUS_ADDRESS, VCNL4020_REGISTER_PROX_RESULT, 2)
    # Convert the data (16 bit value (HEX) -> DEC). High Byte * 256 + Low Byte.
    proximity = data[0] * 256 + data[1]
    #time.sleep(0.001)
    return proximity
 
def streamToSys(proximity):
    sys.stdout.buffer.write(struct.pack('>H', proximity))
    sys.stdout.flush()
 
 
# Open file to save the data from the sensor.
f1=open('./sensor_output.csv', 'w+')
f3=open('./erg.csv', 'w+')
norm = 0.016666
counter = 0
time.sleep(1)
 
 
time_start = time.time()
 
# Program loop.
try:
    while True:
        time_exp = time.time() - time_start
        erg = round(time_exp, 6)
        while (erg > norm):
            proximity = getProximity() 
            #print('step = {0}, proximity = {1}, time_exp = {2}'.format(erg, proximity, time_exp), file = f1)
            streamToSys(proximity)
            norm += 0.016666
            counter += 1
        if (erg >= (round(norm - 0.0085, 6))) and (erg <= (round(norm + 0.0085, 6))):
            proximity = getProximity()      
            streamToSys(proximity)
            #print('step = {0}, proximity = {1}, time_exp = {2}'.format(erg, proximity, time_exp), file = f1)
            norm += 0.016666
            counter += 1
            norm = round(norm, 6)     
except KeyboardInterrupt:
    pass
