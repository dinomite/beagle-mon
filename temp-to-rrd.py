#!/usr/bin/env python
# coding=utf8
import sys
import time
import rrdtool
import Adafruit_BMP.BMP085 as BMP085
from w1thermsensor import W1ThermSensor

rrd_dir = '/home/dinomite/data/'
sensors = {
            'desk': BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES),
            'outside': W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "000005aba36c"),
            'vent': W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, "000005ab8e9c")
        }

#for sensor in W1ThermSensor.get_available_sensors():
    #print("Sensor %s has temperature %.2f°F" % (sensor.id, sensor.get_temperature(W1ThermSensor.DEGREES_F)))

#sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)


def createRRD():
    ret = rrdtool.create(rrdFile, "--step", "60", "--start", '1405042382',
            "DS:temperature:GAUGE:60:50:90",
            "DS:pressure:GAUGE:60:87000:108570",
            # Every minute for a year
            "RRA:AVERAGE:0.5:1:525600",
            # Hourly average, 5 years
            "RRA:AVERAGE:0.5:60:43800",
            # Min annual temperature
            "RRA:MIN:0.5:1440:365",
            # Max annual temperature
            "RRA:MAX:0.5:1440:365")
    if ret:
        print(rrdtool.error())


def readAndStoreAll():
    for name, sensor in sensors.items():
        print("Sensor name: " + name)
        #if isinstance(sensor, W1ThermSensor:
        if type(sensor) is W1ThermSensor:
            print("Sensor %s has temperature %.2f°F" % (sensor.id, sensor.get_temperature(W1ThermSensor.DEGREES_F)))
        else:
            #elif type(sensor) is BMP085:
            temp_in_fahrenheit = sensor.read_temperature() * 1.8 + 32.0
            pressure = sensor.read_pressure()
            print("Temp: %.2f  Pressure: %.2f°F" % (temp_in_fahrenheit, pressure))


def readAndStoreData():
    temp_in_fahrenheit = sensor.read_temperature() * 1.8 + 32.0
    pressure = sensor.read_pressure()
    update = time.strftime('%s') + ':{0:0.2f}:{1:0.2f}'.format(temp_in_fahrenheit, pressure)
    #print time.strftime("%Y-%m-%d %H:%M") + '   ' + update

    ret = rrdtool.update(rrdFile, update);
    if ret:
        print(rrdtool.error())


#createRRD()

#readAndStoreData()

while 1:
    #readAndStoreData()
    readAndStoreAll()
    time.sleep(55)
