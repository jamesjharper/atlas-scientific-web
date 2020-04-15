#!flask/bin/python
import io
default_bus = 1 # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0

from sys import platform

# TODO: implement this for windows if needed, otherwise this is just for running unit tests
if platform == "win32" or platform == "win64":
    class I2CBus:
     
        def __init__(self, bus=default_bus):
            pass

        def ping(self, address):
            return False

        def read(self, address, num_of_bytes=31):
            return '' 

        def write(self, address, value):
            pass

        def close(self):
            pass

else:
    import fcntl
    I2C_SLAVE = 0x703

    class I2CBus:
        
        def __init__(self, bus=default_bus):
            self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
            self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

        def ping(self, address):
            try:
                self.read(address)
                return True
            except IOError:
                return False

        def read(self, address, num_of_bytes=31):
            fcntl.ioctl(self.file_read, I2C_SLAVE, address)
            return self.file_read.read(num_of_bytes)  

        def write(self, address, value):
            fcntl.ioctl(self.file_write, I2C_SLAVE, address)
            self.file_write.write(value)

        def close(self):
            self.file_read.close()
            self.file_write.close()
