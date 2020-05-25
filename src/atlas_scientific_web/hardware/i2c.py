import io
import threading

from sys import platform

default_bus = 1 # the default bus for I2C on the newer Raspberry Pis, certain older boards use bus 0
read_chunk_size = 128

class I2CSessionProvider:
    def __init__(self, bus_io):
        self.bus_io = bus_io
        self.channel_locks_lock = threading.RLock()
        self.file_lock = threading.RLock()
        self.channel_locks = {}

    def acquire_access(self, address, timeout_seconds=30):
        channel_lock = self._get_channel_lock(address)
        return I2CSession(channel_lock,  self.file_lock, self.bus_io, address, timeout_seconds)

    def _get_channel_lock(self, address):
        with self.channel_locks_lock:
            channel_lock = self.channel_locks.get(address, None)
            if not channel_lock:
                channel_lock = threading.RLock()
                self.channel_locks[address] = channel_lock
            return channel_lock

class I2CSession:
    def __init__(self, rx_tx_lock, file_lock, bus_io, address, timeout_seconds):
        self.address = address
        self.bus_io = bus_io
        self.timeout_seconds = timeout_seconds
        self.file_lock = file_lock
        self.rx_tx_lock = rx_tx_lock

    def __enter__(self):
        self.rx_tx_lock.acquire(timeout=self.timeout_seconds)
        return self

    def __exit__(self, type, value, traceback):
        self.rx_tx_lock.release()

    def ping(self):
        with self.file_lock:
            return self.bus_io.ping(self.address)

    def read(self):
        with self.file_lock:
            return self.bus_io.read(self.address)

    def write(self, value):
        with self.file_lock:
            return self.bus_io.write(self.address, value)

# TODO: implement this for windows if needed, otherwise this is just for running unit tests
if platform == "win32" or platform == "win64":
    class I2CBusIo:
     
        def __init__(self, bus=default_bus):
            pass

        def ping(self, address):
            try:
                self.read(address, 1)
                return True
            except IOError:
                return False

        def read(self, address, num_of_bytes=read_chunk_size):
            return ''

        def write(self, address, value):
            pass

        def close(self):
            pass

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()

else:
    import fcntl
    I2C_SLAVE = 0x703

    class I2CBusIo:
        def __init__(self, bus=default_bus):
            self.file_read = io.open("/dev/i2c-"+str(bus), "rb", buffering=0)
            self.file_write = io.open("/dev/i2c-"+str(bus), "wb", buffering=0)

        def ping(self, address):
            try:
                self.read(address, 1)
                return True
            except IOError:
                return False

        def read(self, address, num_of_bytes=read_chunk_size):
            fcntl.ioctl(self.file_read, I2C_SLAVE, address)
            return self.file_read.read(num_of_bytes)

        def write(self, address, value):
            fcntl.ioctl(self.file_write, I2C_SLAVE, address)
            self.file_write.write(value)

        def close(self):
            if self.file_read:
                self.file_read.close()
            self.file_read = None

            if self.file_write:
                self.file_write.close()
            self.file_write = None

        def __enter__(self):
            return self

        def __exit__(self, type, value, traceback):
            self.close()
