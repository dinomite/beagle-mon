#!/usr/bin/env python3
# coding=utf8
import logging
import os
import time

import http.client

import rrdtool
import Adafruit_BMP.BMP085 as BMP085
from w1thermsensor import W1ThermSensor, SensorNotReadyError, NoSensorFoundError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

RRD_DIR = '/home/dinomite/data/'

EMONCMS_HOST = "emon.dinomite.net"
EMONCMS_PORT = 443
EMONCMS_PATH = "/input/post?node=temperature&apikey=" + os.environ['EMONCMS_API_KEY']

BMP085_CORRECTION = -12.5


def get_1w_sensor(sensor_id):
    try:
        return W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    except NoSensorFoundError as e:
        logger.error("Sensor " + sensor_id + " not found", e)
        exit(1)


def convert_celsius_to_fahrenheit(celsius):
    return celsius * 1.8 + 32.0


def write_to_rrd(name, value):
    rrd_file = RRD_DIR + name + ".rrd"
    ret = rrdtool.update(rrd_file, value )
    if ret:
        logger.warn("Couldn't write to RRD: " + rrdtool.error())

def send_to_emoncms(name, temperature):
    path = EMONCMS_PATH + "&fulljson={\"" + name + "_temperature\":" + "{:.1f}".format(temperature) + "}"
    logger.debug("Path: " + path)
    connection = http.client.HTTPSConnection(EMONCMS_HOST, EMONCMS_PORT)
    connection.request("GET", path)
    response = connection.getresponse()
    if response.status != 200:
        logger.warn("Bad response status: " + response.status)


def read_and_store_all():
    for name, sensor in sensors.items():
        logger.debug("Sensor name: " + name)

        if type(sensor) is W1ThermSensor:
            try:
                temperature = sensor.get_temperature(W1ThermSensor.DEGREES_F)
                value = time.strftime('%s') + ':{0:0.2f}'.format(temperature)
                logger.debug("Sensor %s has temperature %.2f°F" % (sensor.id, temperature))
            except SensorNotReadyError as e:
                logger.warn("Sensor " + name + " not ready to read", e)
                continue
        else:
            temperature = convert_celsius_to_fahrenheit(sensor.read_temperature()) + BMP085_CORRECTION
            pressure = sensor.read_pressure()
            value = time.strftime('%s') + ':{0:0.2f}:{1:0.2f}'.format(temperature, pressure)
            logger.debug("Temp: %.2f  Pressure: %.2f°F" % (temperature, pressure))

        write_to_rrd(name, value)
        send_to_emoncms(name, temperature)


logger.debug("Acquiring sensors")
sensors = {
    'desk': BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES),
    'outside': get_1w_sensor("000005aba36c"),
    'vent': get_1w_sensor("000005ab8e9c")
}
logger.debug("Sensor handles created")


logger.info("Beginning monitoring")
while 1:
    read_and_store_all()
    time.sleep(60)
