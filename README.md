Sensor monitoring from a BeagleBoard

# Prerequisites
w1thermsensor
smbus-cffi

# Adafruit_BMP
This uses the [Adafruit Python BMP](https://github.com/adafruit/Adafruit_Python_BMP)
library.  Get it and follow the installation instructions.

# Startup script
Goes in /etc/systemd/system/multi-user.target.wants/temperature.service

Then

    sudo systemctl --system daemon-reload

Manage with:

    sudo systemctl [start/stop] temperature.service
