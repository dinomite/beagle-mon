import sys
import rrdtool
import Adafruit_BMP.BMP085 as BMP085

sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)
rrdFile = '/root/data/temp.rrd'


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
        print rrdtool.error()


def readAndStoreData():
    temp_in_fahrenheit = sensor.read_temperature() * 1.8 + 32.0
    pressure = sensor.read_pressure()
    update = 'N:{0:0.2f}:{0:0.2f}'.format(temp_in_fahrenheit, pressure)

    ret = rrdtool.update(rrdFile, update);
    if ret:
        print rrdtool.error()


#createRRD()
readAndStoreData()
