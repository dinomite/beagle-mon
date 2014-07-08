import sys
import rrdtool
import Adafruit_BMP.BMP085 as BMP085

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

sensor = BMP085.BMP085(mode=BMP085.BMP085_ULTRAHIGHRES)

def createRRD():
    ret = rrdtool.create("temp.rrd", "--step", "300", "--start", '1404780978',
            "DS:temperature:GAUGE:600:50:90",
            # 30 minute rolling average; keep one day
            "RRA:AVERAGE:0.5:6:48",
            # Daily average, keep one year
            "RRA:AVERAGE:0.5:288:365",
            # Min temperature for day
            "RRA:MIN:0.5:1:48",
            # Max temperature for day
            "RRA:MAX:0.5:1:48")
    if ret:
        print rrdtool.error()


temp_in_fahrenheit = sensor.read_temperature() * 1.8 + 32.0
ret = rrdtool.update('temp.rrd','N:' + `temp_in_fahrenheit`);
if ret:
    print rrdtool.error()

#print 'Temp = {0:0.2f} *F'.format(temp_in_fahrenheit)
#print 'Pressure = {0:0.2f} Pa'.format(sensor.read_pressure())

