#!/usr/bin/env python
# coding=utf8
import time
import logging

import rrdtool
import Adafruit_BMP.BMP085 as BMP085
from w1thermsensor import W1ThermSensor, SensorNotReadyError, NoSensorFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

rrd_dir = '/home/dinomite/data/'


def get_1w_sensor(sensor_id):
    try:
        return W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    except NoSensorFoundError as e:
        logger.error("Sensor " + sensor_id + " not found", e)
        exit(1)


logger.debug("Acquiring sensors")
sensors = {
    'desk': BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES),
    'outside': get_1w_sensor("000005aba36c"),
    'vent': get_1w_sensor("000005ab8e9c")
}
logger.debug("Sensor handles created")


def read_and_store_all():
    for name, sensor in sensors.items():
        logger.debug("Sensor name: " + name)

        if type(sensor) is W1ThermSensor:
            try:
                temperature = sensor.get_temperature(W1ThermSensor.DEGREES_F)
            except SensorNotReadyError as e:
                logger.warn("Sesnor " + name + " not ready to read", e)

            update = time.strftime('%s') + ':{0:0.2f}'.format(temperature)
            logger.debug("Sensor %s has temperature %.2f°F" % (sensor.id, temperature))
        else:
            temperature = sensor.read_temperature() * 1.8 + 32.0
            pressure = sensor.read_pressure()
            update = time.strftime('%s') + ':{0:0.2f}:{1:0.2f}'.format(temperature, pressure)
            logger.debug("Temp: %.2f  Pressure: %.2f°F" % (temperature, pressure))

        rrd_file = rrd_dir + name + ".rrd"
        ret = rrdtool.update(rrd_file, update)
        if ret:
            logger.warn("Couldn't write to RRD: " + rrdtool.error())


logger.info("Beginning monitoring")
while 1:
    read_and_store_all()
    time.sleep(55)
