#!flask/bin/python

from enum import Enum

class AtlasScientificError(Exception):
    pass

class AtlasScientificDeviceNotReadyError(AtlasScientificError):
    pass

class AtlasScientificSyntaxError(AtlasScientificError):
    pass

class AtlasScientificNoDeviceAtAddress(AtlasScientificError):
    pass

class AtlasScientificDeviceNotYetSupported(AtlasScientificError):
    pass

class AtlasScientificResponseSyntaxError(AtlasScientificError):

    def __init__(self, felid, message):
        self.felid = felid
        self.message = message

class RequestValidationError(Exception):
    pass

class RequestResult(Enum):
    OK = 1
    SYNTAX_ERROR = 2
    NOT_READY = 254
    ACK = 255  # ok with no message response body

class AtlasScientificResponse(object):
    def __init__(self, response_bytes, response_timestamp):
        self.response_timestamp = response_timestamp

        try:
            self.status = RequestResult(response_bytes[0])
        except Exception as err:
            raise AtlasScientificResponseSyntaxError('status', str(err))
        
        try:
            if self.status == RequestResult.OK:
                # omit first byte, as it's the status bytes,
                # find the response length to strip the unused data
                length = AtlasScientificResponse.__find_response_length(response_bytes)
                self.attributes = response_bytes[1:length].decode('ascii').split(",")
            else:
                self.attributes = []
        except Exception as err:
            raise AtlasScientificResponseSyntaxError('body', str(err))


    def get_field(self, name, index):
        try:
            return self.attributes[index]
        except IndexError:
            raise AtlasScientificResponseSyntaxError(name, "expected field missing from response")
        except Exception as err:
            raise AtlasScientificResponseSyntaxError(name, str(err))

    def get_fields(self, name, start, end):
        try:
            return self.attributes[start:end]
        except IndexError:
            raise AtlasScientificResponseSyntaxError(name, "expected fields missing from response")
        except Exception as err:
            raise AtlasScientificResponseSyntaxError(name, str(err))

    @staticmethod
    def __find_response_length(response_bytes):
        # omit content after the first x00, as the device
        # may return more bytes then expected.
        l = response_bytes.find(b'\x00')
        # if no x00 was found, assume all bytes contain data
        return l if l != -1 else None

class AtlasScientificDeviceOutput(object): 
    def __init__(self, device_response):
        # expected format ?O,%,MG"
        self.units = device_response.get_fields('output', 1, None)    

class AtlasScientificDeviceInfo(object): 
    def __init__(self, device_response, address):
        self.device_type = device_response.get_field('device_type', 1)
        self.version = device_response.get_field('version', 2)
        self.address = address
        self.vendor = 'atlas-scientific'

class AtlasScientificDeviceSample(object): 
    def __init__(self, symbol, value, value_type, timestamp, unit_code):
        self.symbol = symbol
        self.value = value
        self.value_type = value_type
        self.timestamp = timestamp
        self.unit_code = unit_code

    @staticmethod
    def from_expected_device_output(device_response, expected_output_units):
        result = []
        unit_index = 0
        for unit in expected_output_units:
            value = device_response.get_field('sample', unit_index)
            result.append(AtlasScientificDeviceSample(unit.symbol, value, unit.value_type, device_response.response_timestamp, unit.unit_code))
            unit_index = unit_index + 1
        return result

class AtlasScientificDeviceCompensationFactor(object): 
    def __init__(self, factor, symbol, value):
        self.factor = factor
        self.symbol = symbol
        self.value = value

class AtlasScientificDeviceCalibrationPoint(object): 
    def __init__(self, point, actual_value = None ):
        self.point = point
        self.actual_value = actual_value

class AtlasScientificDeviceConfigurationParameter(object): 
    def __init__(self, parameter, value):
        self.parameter = parameter
        self.value = value

class ExpectedValueType(object):
    def __init__(self, expected_value_type):
        if expected_value_type:
            self.t = expected_value_type
        else:
            self.t = "none"
    
    @property
    def is_none(self):
        return self.t == "none"

    def validate_is_of_type(self, value):
        try:
            if not value:
                if self.t == "none":
                    return None
                raise RequestValidationError

            elif self.t == "float":
                float(value)
            elif self.t == "int":
                int(value)
            elif self.t == "string":
                pass
            elif self.t == "bool":
                if value.lower() in ['false', '0','no']:
                    return '0'
                if value.lower() in ['true', '1','yes']:
                    return '1'
                raise RequestValidationError  
            
            return value
        except ValueError:
            raise RequestValidationError