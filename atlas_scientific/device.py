#!flask/bin/python
import logging
import time
import sys

from datetime import datetime, timezone
from i2c import I2CBus
from .models import *
from .capabilities import get_device_capabilities
import sys

class AtlasScientificDeviceBus(object):
    def __init__(self, i2cbus):
        self.i2cbus = i2cbus
        self.known_devices = {}

    def forget_known_devices(self):
        logging.info('Forgeting known devices.')
        self.known_devices = {}

    def scan_for_devices(self):
        logging.info('Scaning for devices.')
        self.forget_known_devices()

        for address in range (0,128):
            try:
                self.__connect_device(address)
            except Exception:
                pass

    def get_known_devices(self):
        return self.known_devices.values()

    def get_device_by_address(self, address):
        device = self.known_devices.get(address, None)
        if device is None: 
            return self.__connect_device(address)
        return device

    def __connect_device(self, address):      
        device = AtlasScientificDevice.connect(self.i2cbus, address)
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
    def connect(i2cbus, address):
        device_log = logging.getLogger(f'I2CDevice[{address}]')  

        if not i2cbus.ping(address):
            raise AtlasScientificNoDeviceAtAddress

        try:
            # Try read device info,
            # if it fails we assume the device vendor isn't atlas scientific
            return AtlasScientificDevice(i2cbus, address)
        except AtlasScientificDeviceNotYetSupported as err:
            device_log.info('Non supported atlas scientific device found.')
            raise err
        except Exception as err:
            device_log.debug(f'Failed to connection device, {err}')
            device_log.info('non atlas scientific device found')
            raise err

    def get_device_info(self):
        return self.device_info

    def get_supported_compensation_factors(self):
        if self.capabilities.compensation:
            return self.capabilities.compensation.factors
        else:
            return {}

    def get_supported_output_measurements(self):
        if self.capabilities.read.output:
            return self.capabilities.read.output
        return []

    def get_supported_calibration_points(self):
        if self.capabilities.calibration:
            return self.capabilities.calibration.points
        return []

    def get_supported_configuration_parameters(self):
        if self.capabilities.configuration:
            return self.capabilities.configuration.parameters
        return {}

    def set_configuration_parameter(self, parameter_details):
        parameter = self.__get_configuration_parameter(parameter_details)
        value = parameter.value_type.validate_is_of_type(parameter_details.value)
        self.__query(f'{parameter.command},{value}', self.device_request_latency)

    def get_enabled_output_measurements(self):
        if self.current_output_measurements is not None:
            return self.current_output_measurements

        # non output device
        elif self.capabilities.read == None:
            self.current_output_measurements = []

        # single output device
        elif len(self.capabilities.read.output) <= 1:
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
        # find all the measurements which currently are enabled, and need to be disabled
        supported_units = set(m.unit_code for m in self.get_supported_output_measurements())
        current_enabled_units = set(m.unit_code for m in self.get_enabled_output_measurements())
        requested_units_to_enable = set((u.upper() for u in units))

        units_to_disable = current_enabled_units - requested_units_to_enable
        units_to_enable = requested_units_to_enable - current_enabled_units
        unsupported_units = units_to_enable - supported_units

        if not len(unsupported_units) is 0:
            raise RequestValidationError

        for unit in units_to_enable:
            self.__query_o_enable(unit)

        for unit in units_to_disable:
            self.__query_o_disable(unit)
        
    def read_sample(self, compensation_factors):
        
        explicit_cf = []
        temperature_cf = None

        for cf in compensation_factors:
            # Currently the only documented compensation factors
            # which can be rolled into the read command
            # this code assume you have the lastest firmware on your device
            if cf.factor.lower() == "temperature":
                temperature_cf = cf
            else:
                explicit_cf.append(cf)

        if explicit_cf:
            self.set_measurement_compensation_factors(explicit_cf)

        if temperature_cf:
            factor = self.__get_measurement_compensation_factor(temperature_cf)
            value = factor.value_type.validate_is_of_type(temperature_cf.value)

            return self.__query_rt(value)
        else:
            return self.__query_r()

    def set_measurement_compensation_factors(self, compensation_factors):

        for compensation_factor in compensation_factors:
            factor = self.__get_measurement_compensation_factor(compensation_factor)
            value = factor.value_type.validate_is_of_type(compensation_factor.value)

            self.__query(f'{factor.command},{value}', self.device_request_latency)

    def set_calibration_point(self, calibration):
        points = self.get_supported_calibration_points()
        
        cal_point = next((p for p in points if insensitive_eq(p.id, calibration.point)), None)
        
        if not cal_point:
            raise RequestValidationError

        cal_request = 'Cal'
        if cal_point.sub_command:
            cal_request = f"{cal_request},{cal_point.sub_command}"

        if not cal_point.value_type.is_none:
            value = cal_point.value_type.validate_is_of_type(calibration.actual_value)
            cal_request = f"{cal_request},{value}"

        return self.__query(cal_request, self.capabilities.calibration.latency)

    def __get_measurement_compensation_factor(self, compensation_factor):
        factors = self.get_supported_compensation_factors()
        factor = factors.get(compensation_factor.factor.lower(), None)
         
        if not factor: 
            raise RequestValidationError

        if not insensitive_eq(factor.symbol, compensation_factor.symbol):
            raise RequestValidationError
    
        return factor

    def __get_configuration_parameter(self, parameter_details):
        parameters = self.get_supported_configuration_parameters()
        parameter = parameters.get(parameter_details.parameter.lower(), None)
         
        if not parameter: 
            raise RequestValidationError
    
        return parameter

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
        result = self.__query('r', self.capabilities.read.latency)
        return AtlasScientificDeviceSample.from_expected_device_output(result, output_units)

    def __query_rt(self, temperature): 
        output_units = self.get_enabled_output_measurements()
        result = self.__query(f'rt,{temperature}', self.capabilities.read.latency)
        return AtlasScientificDeviceSample.from_expected_device_output(result, output_units)

    def __query(self, query, process_delay):
        query_bytes = query.encode('ascii') + b'\00'
        self.device_log.debug(f' TX   >> {query_bytes}')
        self.i2cbus.write(self.address, query_bytes)

        # back off by 1/3 when data not ready
        wait_durations = [
            process_delay, 
            process_delay / 3, 
            process_delay / 3,
            process_delay / 3,
        ]

        for wait_duration in wait_durations:
            response = self.__wait_and_read(wait_duration)
            if response.status != RequestResult.NOT_READY:
                return response

        raise AtlasScientificDeviceNotReadyError

    def __wait_and_read(self, process_delay):
        self.device_log.debug(f' WAIT :: {process_delay}')
        time.sleep(process_delay)
        data = self.i2cbus.read(self.address)
        self.device_log.debug(f' RX   << {data}')

        response =  AtlasScientificResponse(data, get_datetime_now(timezone.utc))
        if response.status == RequestResult.SYNTAX_ERROR:
            raise AtlasScientificSyntaxError
        return response
    
def insensitive_eq(a, b):
    return a.lower() == b.lower()

# code stem needed to unit test date times
def get_datetime_now(tz):
    return datetime.now(tz)


