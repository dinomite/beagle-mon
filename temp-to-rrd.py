#!/usr/bin/env python
# coding=utf8
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

def create_desk_rrd():
    ret = rrdtool.create(rrd_dir + "desk.rrd", "--step", "60", "--start", '1405042382',
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
        print("Error creating RRD: " + rrdtool.error())

def create_1w_rrd(filename):
    ret = rrdtool.create(rrd_dir + filename + ".rrd", "--step", "60", "--start", '1405042382',
                         "DS:temperature:GAUGE:60:50:90",
                         # Every minute for a year
                         "RRA:AVERAGE:0.5:1:525600",
                         # Hourly average, 5 years
                         "RRA:AVERAGE:0.5:60:43800",
                         # Min annual temperature
                         "RRA:MIN:0.5:1440:365",
                         # Max annual temperature
                         "RRA:MAX:0.5:1440:365")
    if ret:
        print("Error creating RRD: " + rrdtool.error())

# create_desk_rrd()
# create_1w_rrd("outside")
# create_1w_rrd("vent")
# exit(0)

def read_and_store_all():
    for name, sensor in sensors.items():
        # print("Sensor name: " + name)

        if type(sensor) is W1ThermSensor:
            temperature = sensor.get_temperature(W1ThermSensor.DEGREES_F)
            update = time.strftime('%s') + ':{0:0.2f}'.format(temperature)
            # print("Sensor %s has temperature %.2f°F" % (sensor.id, temperature))
        else:
            temperature = sensor.read_temperature() * 1.8 + 32.0
            pressure = sensor.read_pressure()
            update = time.strftime('%s') + ':{0:0.2f}:{1:0.2f}'.format(temperature, pressure)
            # print("Temp: %.2f  Pressure: %.2f°F" % (temperature, pressure))

        rrd_file = rrd_dir + name + ".rrd"
        ret = rrdtool.update(rrd_file, update)
        if ret:
            print("Error writing RRD: " + rrdtool.error())

while 1:
    read_and_store_all()
    time.sleep(55)
