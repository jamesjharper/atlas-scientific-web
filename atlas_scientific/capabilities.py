from .models import AtlasScientificDeviceNotYetSupported

device_capabilities = {
    "pH": {
        "reading": {
            "reading_latency":  0.9,
            "output": [
                {
                    "symbol": "pH",
                    "unit": "Power of Hydrogen",
                    "value_type": "float"
                }
            ],
        },
        "compensation": [
            {
                "factor": "Temperature",
                "symbol": "°C",
                "unit": "degrees Celsius",
                "command": "T",
                "value_type": "float"
            },
        ],
    },
    "ORP": {
        "reading": {
            "reading_latency":  0.9,
            "output": [
                {
                    "symbol": "mV",
                    "unit": "millivolt",
                    "value_type": "float"
                }
            ],
        },
    },
    "DO": {
        "reading": {
            "reading_latency":  0.9,
            "output": [
                {
                    "symbol": "%",
                    "unit": "Percent saturation",
                    "value_type": "float"
                },
                {
                    "symbol": "mg/L", 
                    "unit": "milligram per litre",
                    "unit_code": "mg",
                    "value_type": "float"
                }
            ],
        },
        "compensation": [
            {
                "factor": "Salinity",
                "symbol": "μS",
                "unit": "microsiemens",
                "command": "S",
                "value_type": "float"
            },
            {
                "factor": "Pressure",
                "symbol": "kPa",
                "unit": "kilopascal",
                "command": "P",
                "value_type": "float"
            },
            {
                "factor": "Temperature",
                "symbol": "°C",
                "unit": "degrees Celsius",
                "command": "T",
                "value_type": "float"
            },
        ],
    },
    "CO2": {
        "reading": {
            "reading_latency":  0.9,
        },
    },
}

def get_device_capabilities(device_type):
    caps = device_capabilities.get(device_type, None)
    if not caps:
        raise AtlasScientificDeviceNotYetSupported
    return DeviceCapabilities(caps)

class DeviceCapabilities(object): 
    def __init__(self, capabilities_dict):
        if "reading" in capabilities_dict:
            self.reading = ReadingCapabilities(capabilities_dict["reading"])
        else:
            self.reading = None

        if "compensation" in capabilities_dict:
            self.compensation = MeasurementCompensationCapabilities(capabilities_dict["compensation"])
        else:
            self.compensation = None

class ReadingCapabilities(object): 
    def __init__(self, capabilities_dict):
        # use default of 0.9 second if not defined 
        self.reading_latency = capabilities_dict.get("reading_latency", 0.9) 
        self.output = MeasurementCapabilities(capabilities_dict.get("output", []))

class MeasurementCapabilities(object): 
    def __init__(self, capabilities_dict):
        self.units = list(MessureCapability(unit) for unit in capabilities_dict)

class MessureCapability(object): 
    def __init__(self, capabilities_dict):
        self.unit = capabilities_dict.get("unit", "")
        # default to string if not set, as this is a safe to parse
        # and could end up working with the device query by chance 
        self.value_type = capabilities_dict.get("value_type", "string")
        self.symbol = capabilities_dict.get("symbol", "")

        # this is the value which will be given the the device for each command 
        # in respect to this unit. By default it is the same as the symbol,
        # however it is sometimes diffrent 

        # {x},? request always returns units in upper case
        self.unit_code = capabilities_dict.get("unit_code", self.symbol).upper()

class MeasurementCompensationCapabilities(object): 
    def __init__(self, compensation_dict):
        factors = (MeasurementCompensationCapability(unit) for unit in compensation_dict)
        self.factors = {f.factor:f for f in factors}

class MeasurementCompensationCapability(object): 
    def __init__(self, compensation_dict):

        # TODO: throw error when this value is missing
        self.factor = compensation_dict.get("factor", "").lower()

        # TODO: throw error when this value is missing
        self.command = compensation_dict.get("command", "")
    
        # default to string if not set, as this is a safe to parse
        # and could end up working with the device query by chance 
        self.value_type = compensation_dict.get("value_type", "string")

        self.symbol = compensation_dict.get("symbol", "")
        self.unit = compensation_dict.get("unit", "")
        