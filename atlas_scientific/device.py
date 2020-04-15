#!flask/bin/python
import logging
import time
import sys

from datetime import datetime, timezone
from i2c import I2CBus
from .models import RequestResult, AtlasScientificResponse, AtlasScientificDeviceInfo, AtlasScientificDeviceSample, AtlasScientificDeviceOutput
from .capabilities import get_device_capabilities
import sys

class AtlasScientificDeviceBus(object):
    def __init__(self, i2cbus):
        self.i2cbus = i2cbus
        self.known_devices = {}

    def forget_known_devices(self):
        logging.info('Forgeting known devices.')
        # clear perviously known devices
        self.known_devices = {}

    def scan_for_devices(self):
        logging.info('Scaning for devices.')
        self.forget_known_devices()

        for address in range (0,128):
            self.try_connect_device(address)

    def get_known_devices(self):
        return self.known_devices.values()

    def get_device_by_address(self, address):
        device = self.known_devices.get(address, None)
        if device is None: 
            return self.try_connect_device(address)
        return device

    def try_connect_device(self, address):      
        device = AtlasScientificDevice.try_connect(self.i2cbus, address)
        if device is not None: 
            device_info = device.get_device_info()
            logging.debug(f'{device_info.device_type} device found at address {device_info.address}')
            self.known_devices[address] = device
        return device

class AtlasScientificDevice(object):
    def __init__(self, i2cbus, address):

        self.device_log = logging.getLogger(f'AtlasScientificDevice[{address}]')
        self.i2cbus = i2cbus
        self.address = address
        self.device_request_latency = 0.3
        self.device_info = None
        self.current_output_measurements = None
        self.capabilities = None
        self.__connect()

    def __connect(self):
        self.device_info = self.__query_i()
        self.capabilities = get_device_capabilities(self.device_info.device_type)

    @staticmethod
    def try_connect(i2cbus, address):
        if not i2cbus.ping(address):
            return None
        try:
            # Try read device info,
            # if it fails we assume the device vendor isn't atlas scientific
            return AtlasScientificDevice(i2cbus, address)
        except Exception as err:
            device_log = logging.getLogger(f'I2CDevice[{address}]')  
            device_log.debug(f'failed to connection device, {err}')
            device_log.info('non atlas scientific device found')
            return None

    def get_device_info(self):
        return self.device_info

    def get_supported_compensation_factors(self):
        if self.capabilities.compensation:
            return self.capabilities.compensation.factors
        else:
            return {}

    def get_supported_output_measurements(self):
        return self.capabilities.reading.output.units

    def get_enabled_output_measurements(self):
        if self.current_output_measurements is not None:
            return self.current_output_measurements

        # non output device
        elif self.capabilities.reading == None:
            self.current_output_measurements = []

        # single output device
        elif len(self.capabilities.reading.output.units) <= 1:
            self.current_output_measurements = self.get_supported_output_measurements()

        # multi output device
        else:          
            supported_unit_codes = {u.unit_code:u for u in self.get_supported_output_measurements()}
            
            # Read the device's current output
            result = self.__query_o()

            # order must be presserved as this is the same order the device will list the values back with the 'r' command
            self.current_output_measurements = list([u for u in [supported_unit_codes.get(ui, None) for ui in result.units] if u])

        return self.current_output_measurements

    def set_enabled_output_measurements(self, units):
        # find all the measurements which currently enabled, and need to be disabled
        current_enabled_units = set(m.unit_code for m in self.get_enabled_output_measurements())
        requested_units_to_enable = set((u.upper() for u in units))

        units_to_disable = current_enabled_units - requested_units_to_enable
        units_to_enable = requested_units_to_enable - current_enabled_units

        for unit in units_to_enable:
            self.__query_o_enable(unit)

        for unit in units_to_disable:
            self.__query_o_disable(unit)
        
    def read_sample(self, compensation_factors):
        
        explicit_cf = []
        temperature_cf = None

        for cf in compensation_factors:
            # Currently the only documented compensation factors
            # which can be rolled in to the read command
            if cf.factor.lower() == "temperature":
                temperature_cf = cf
            else:
                explicit_cf.append(cf)

        if explicit_cf:
            self.set_measurement_compensation_factors(explicit_cf)

        if temperature_cf:
            return self.__query_rt(temperature_cf.value)
        else:
            return self.__query_r()

    def set_measurement_compensation_factors(self, compensation_factors):
        factors = self.get_supported_compensation_factors()

        for compensation_factor in compensation_factors:
            # TODO: return error when no match
            command = factors.get(compensation_factor.factor.lower(), None).command
            self.__query(f'{command},{compensation_factor.value}', self.device_request_latency)

    def __invalidate_output_measurements_cache(self):
        self.current_output_measurements = None # flag for lazy update

    def __query_i(self): 
        result = self.__query('i', self.device_request_latency)
        return AtlasScientificDeviceInfo(result, self.address)

    def __query_o_enable(self, unit):
        self.__invalidate_output_measurements_cache()
        return self.__query(f'o,{unit},1', self.device_request_latency)

    def __query_o_disable(self, unit):
        self.__invalidate_output_measurements_cache()
        return self.__query(f'o,{unit},0', self.device_request_latency)

    def __query_o(self): 
        result = self.__query('o,?', self.device_request_latency)
        return AtlasScientificDeviceOutput(result)

    def __query_r(self): 
        output_units = self.get_enabled_output_measurements()
        result = self.__query('r', self.capabilities.reading.reading_latency)
        return AtlasScientificDeviceSample.from_expected_device_output(result, output_units)

    def __query_rt(self, temperature): 
        output_units = self.get_enabled_output_measurements()
        result = self.__query(f'rt,{temperature}', self.capabilities.reading.reading_latency)
        return AtlasScientificDeviceSample.from_expected_device_output(result, output_units)

    def __query(self, query, process_delay):
        query_bytes = query.encode('ascii') + b'\00'
        self.device_log.debug(f' TX   >> {query_bytes}')

        self.i2cbus.write(self.address, query_bytes)
        self.device_log.debug(f' WAIT :: {process_delay}')
        time.sleep(process_delay)
        data = self.i2cbus.read(self.address)
        self.device_log.debug(f' RX   << {data}')

        # TODO: add re attempt if NOT_READY returned
        return AtlasScientificResponse(data, get_datetime_now(timezone.utc))

# code stem needed to unit test date times
def get_datetime_now(tz):
    return datetime.now(tz)