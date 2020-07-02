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
logger.setLevel(os.getenv('LOG_LEVEL', logging.INFO))

RRD_DIR = '/home/dinomite/data/'

EMONCMS_HOST = "emon.dinomite.net"
EMONCMS_PORT = 443
EMONCMS_PATH = "/input/post?node=environment&apikey=" + os.environ['EMONCMS_API_KEY']


def get_1w_sensor(sensor_id):
    try:
        return W1ThermSensor(W1ThermSensor.THERM_SENSOR_DS18B20, sensor_id)
    except NoSensorFoundError as e:
        logger.error("Sensor " + sensor_id + " not found", e)
        pass


def convert_celsius_to_fahrenheit(celsius):
    return celsius * 1.8 + 32.0


def write_to_rrd(name, temperature, pressure=None):
    value = time.strftime('%s') + ':{}'.format(temperature)
    if pressure:
        value += ':{}'.format(pressure)
    logger.debug("RRD update: " + value)

    rrd_file = RRD_DIR + name + ".rrd"
    ret = rrdtool.update(rrd_file, value)
    if ret:
        logger.warn("Couldn't write to RRD: " + rrdtool.error())

def send_to_emoncms(name, temperature, pressure=None):
    value = '&fulljson={"' + name + '_temperature":' + str(temperature)
    if pressure:
        value += ',"' + name + '_pressure":' + str(pressure)
    value += "}"
    logger.debug("Value: " + value)

    connection = http.client.HTTPSConnection(EMONCMS_HOST, EMONCMS_PORT)
    connection.request("GET", EMONCMS_PATH + value)
    response = connection.getresponse()
    if response.status != 200:
        logger.warn("Bad response status: " + response.status)


def read_and_store_all():
    for name, (sensor, correction) in sensors.items():
        logger.debug("Sensor name: " + name)

        if type(sensor) is W1ThermSensor:
            try:
                temperature = round(correction(sensor.get_temperature(W1ThermSensor.DEGREES_F)))
                pressure = None
                logger.debug("{} ({}) temperature: {}°F".format(name, sensor.id, temperature))
            except SensorNotReadyError as e:
                logger.warn("Sensor " + name + " not ready to read", e)
                continue
        else:
            temperature = round(correction(convert_celsius_to_fahrenheit(sensor.read_temperature())))
            pressure = round(sensor.read_pressure() / 100)
            logger.debug("{} (BMP085) temperature: {}°F  pressure: {}hPa".format(name, temperature, pressure))

        send_to_emoncms(name, temperature, pressure)
        write_to_rrd(name, temperature, pressure)


logger.debug("Acquiring sensors")
sensors = {
    'desk': (BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES), lambda x: x - 10 ),
    'outside': (get_1w_sensor("000005aba36c"), lambda x: x + 3),
    'vent': (get_1w_sensor("000005ab8e9c"), lambda x: x + 1),
    'basement_hvac_input': (get_1w_sensor("0416565308ff"), lambda x: x),
    'basement_hvac_output': (get_1w_sensor("000008e3a7d2"), lambda x: x)
}
logger.debug("Sensor handles created")


logger.info("Beginning monitoring")
while 1:
    start = time.time()
    read_and_store_all()
    end = time.time()
    logger.info("Iteration took {} seconds".format(end - start))
    time.sleep(55)
