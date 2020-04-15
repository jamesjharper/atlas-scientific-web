#!flask/bin/python

from enum import Enum

class RequestResult(Enum):
    OK = 1
    SYNTAX_ERROR = 2
    NOT_READY = 254
    ACK = 255  # ok with no message response body

class AtlasScientificResponse(object):
    def __init__(self, response_bytes, response_timestamp):
        self.status = RequestResult(response_bytes[0])
        self.response_timestamp = response_timestamp

        if self.status == RequestResult.OK:
            # omit first byte, as it's the status bytes,
            # omit last byte as its a terminating null zero
            self.attributes = response_bytes[1:-1].decode('ascii').split(",")
        else:
            self.attributes = []

class AtlasScientificDeviceOutput(object): 
    def __init__(self, device_response):
        # expected format ?O,%,MG"
        self.units = device_response.attributes[1:]

class AtlasScientificDeviceInfo(object): 
    def __init__(self, device_response, address):
        self.device_type = device_response.attributes[1]
        self.version = device_response.attributes[2]
        self.address = address
        self.vendor = 'atlas-scientific'

class AtlasScientificDeviceSample(object): 
    def __init__(self, symbol, value, value_type, timestamp):
        self.symbol = symbol
        self.value = value
        self.value_type = value_type
        self.timestamp = timestamp

    @staticmethod
    def from_expected_device_output(device_response, expected_output_units):

        result = []
        unit_index = 0
        for unit in expected_output_units:
            # TODO: write test to break non float
            value = float(device_response.attributes[unit_index])
            result.append(AtlasScientificDeviceSample(unit.symbol, value, unit.value_type, device_response.response_timestamp))
            unit_index = unit_index + 1

        return result

class AtlasScientificDeviceCompensationFactors(object): 
    def __init__(self, device_compensation_factors):      
        factors = (AtlasScientificDeviceCompensationFactor(f) for f in device_compensation_factors)
        self.factors = {f.factor:f for f in factors}

class AtlasScientificDeviceCompensationFactor(object): 
    def __init__(self, device_compensation_factor):
        
        # TODO: throw error if values are missing
        self.factor = device_compensation_factor.get('factor', None)
        self.symbol = device_compensation_factor.get('symbol', None)
        self.value = device_compensation_factor.get('value', None)