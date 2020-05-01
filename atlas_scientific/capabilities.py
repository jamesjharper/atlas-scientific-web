from .models import AtlasScientificDeviceNotYetSupported, ExpectedValueType

device_capabilities = {
    "pH": {
        "read": {
            "latency":  0.9,
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
        "calibration": {
            "latency":  0.9,
            "start_points": ["mid"],
            "points": [
                {
                    "id": "mid",
                    "description": "Single point calibration at midpoint",
                    "value_type": "float",
                    "sub_command": "mid",
                    "next_points": ["low", "Complete"],
                },
                {
                    "id": "low",
                    "description": "Two point calibration at lowpoint",
                    "value_type": "float",
                    "sub_command": "low",
                    "next_points": ["high", "Complete"],
                },
                {
                    "id": "high",
                    "description": "Three point calibration at highpoint",
                    "value_type": "float",
                    "sub_command": "high",
                    "next_points": ["Complete"],
                }
            ]
        },
        "configuration": [
            {
                "parameter": "Name",
                "description": "The name of the device",
                "command": "name",
                "value_type": "string"
            },
            {
                "parameter": "LED",
                "description": "Enabled/Disables the device's indicator LED's",
                "command": "L",
                "value_type": "bool"
            },
        ]
    },
    "ORP": {
        "read": {
            "latency":  0.9,
            "output": [
                {
                    "symbol": "mV",
                    "unit": "millivolt",
                    "value_type": "float"
                }
            ],
        },
        "calibration": {
            "latency":  0.9,
            "start_points": ["any"],
            "points": [
                {
                    "id": "any",
                    "description": "calibrates the ORP circuit to a set value",
                    "value_type": "float",
                    "sub_command": None,
                    "next_points": ["Complete"],
                }
            ]
        },
        "configuration": [
            {
                "parameter": "Name",
                "description": "The name of the device",
                "command": "name",
                "value_type": "string"
            },
            {
                "parameter": "LED",
                "description": "Enabled/Disables the device's indicator LED's",
                "command": "L",
                "value_type": "bool"
            },
        ]
    },
    "DO": {
        "read": {
            "latency":  0.6,
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
                "symbol": u'\u03bcS',
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
        "calibration": {
            "latency":  1.3,
            "start_points": ["atmospheric"],
            "points": [
                {
                    "id": "atmospheric",
                    "description": "Calibrate to atmospheric oxygen levels",
                    "value_type": None,
                    "sub_command": None,
                    "next_points": ["0", "Complete"],
                },
                {
                    "id": "0",
                    "description": "Calibrate device to 0% dissolved oxygen",
                    "value_type": None,
                    "sub_command": "0",
                    "next_points": ["Complete"],
                }
            ]
        },
        "configuration": [
            {
                "parameter": "Name",
                "description": "The name of the device",
                "command": "name",
                "value_type": "string"
            },
            {
                "parameter": "LED",
                "description": "Enabled/Disables the device's indicator LED's",
                "command": "L",
                "value_type": "bool"
            }
        ]
    },
    "EC": {
        "read": {
            "latency":  0.6,
            "output": [
                {
                    "symbol": "EC", 
                    "unit": "Conductivity",
                    "unit_code": "EC",
                    "value_type": "float"
                },
                {
                    "symbol": "T.D.S.", 
                    "unit": "Total Dissolved Solids",
                    "unit_code": "TDS",
                    "value_type": "float"
                },
                {
                    "symbol": u'\u03bcS', 
                    "unit": "microsiemens",
                    "unit_code": "S",
                    "value_type": "float"
                },
                {
                    "symbol": "S.G.", 
                    "unit": "Specific Gravity",
                    "unit_code": "SG",
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
        "calibration": {
            "latency":  0.6,
            "start_points": ["dry"],
            "points": [
                {
                    "id": "dry",
                    "description": "Dry calibration",
                    "value_type": None,
                    "sub_command": "dry",
                    "next_points": ["any", "low"],
                },
                {
                    "id": "any",
                    "description": "Single point calibration of any known conductivity",
                    "value_type": "float",
                    "sub_command": None,
                    "next_points": ["Complete"],
                },
                {
                    "id": "low",
                    "description": "Low end calibration of any known low conductivity",
                    "value_type": "float",
                    "sub_command": "low",
                    "next_points": ["high"],
                },
                {
                    "id": "high",
                    "description": "High end calibration of any known high conductivity",
                    "value_type": "float",
                    "sub_command": "high",
                    "next_points": ["Complete"],
                }
            ]
        },
        "configuration": [
            {
                "parameter": "Name",
                "description": "The name of the device",
                "command": "name",
                "value_type": "string"
            },
            {
                "parameter": "LED",
                "description": "Enabled/Disables the device's indicator LED's",
                "command": "L",
                "value_type": "bool"
            },
            {
                "parameter": "K",
                "description": "Conductivity of probe",
                "command": "K",
                "value_type": "float"
            },
        ]
    },
    "CO2": {
        "read": {
            "latency":  0.9,
            "output": [
                {
                    "symbol": "ppm",
                    "unit": "Gaseous CO2",
                    "unit_code": "ppm",
                    "value_type": "int"
                },
                {
                    "symbol": "°C", 
                    "unit": "Internal device temperature",
                    "unit_code": "t",
                    "value_type": "float"
                },
            ],
        },
        "configuration": [
            {
                "parameter": "Name",
                "description": "The name of the device",
                "command": "name",
                "value_type": "string"
            },
            {
                "parameter": "LED",
                "description": "Enabled/Disables the device's indicator LED's",
                "command": "L",
                "value_type": "bool"
            },
        ]
    },
}

def get_device_capabilities(device_type):
    caps = device_capabilities.get(device_type, None)
    if not caps:
        raise AtlasScientificDeviceNotYetSupported
    return DeviceCapabilities(caps)

class DeviceCapabilities(object): 
    def __init__(self, capabilities_dict):

        if "read" in capabilities_dict:
            self.read = ReadCapabilities(capabilities_dict["read"])
        else:
            self.read = None

        if "compensation" in capabilities_dict:
            self.compensation = CompensationCapabilities(capabilities_dict["compensation"])
        else:
            self.compensation = None

        if "calibration" in capabilities_dict:
            self.calibration = CalibrationCapabilities(capabilities_dict["calibration"])
        else:
            self.calibration = None

        if "configuration" in capabilities_dict:
            self.configuration = ConfigurationCapabilities(capabilities_dict["configuration"])
        else:
            self.configuration = None

class ReadCapabilities(object): 
    def __init__(self, capabilities_dict):
        # use default of 0.9 second if not defined 
        self.latency = capabilities_dict.get("latency", 0.9)
        self.output = list(MessureCapability(unit) for unit in capabilities_dict.get("output", []))
        

class MessureCapability(object): 
    def __init__(self, capabilities_dict):
        self.unit = capabilities_dict.get("unit", "")
        self.value_type = capabilities_dict.get("value_type", "")
        self.symbol = capabilities_dict.get("symbol", "")

        # this is the value which will be given the the device for each command 
        # in respect to this unit. By default it is the same as the symbol,
        # however it is sometimes diffrent 

        # {x},? request always returns units in upper case
        self.unit_code = capabilities_dict.get("unit_code", self.symbol).upper()

class CompensationCapabilities(object): 
    def __init__(self, compensation_dict):
        factors = (CompensationCapability(unit) for unit in compensation_dict)
        self.factors = {f.factor:f for f in factors}

class CompensationCapability(object): 
    def __init__(self, compensation_dict):

        # TODO: throw error when this value is missing
        self.factor = compensation_dict.get("factor", "").lower()

        # TODO: throw error when this value is missing
        self.command = compensation_dict.get("command", "")
    
        # default to string if not set, as this is a safe to parse
        # and could end up working with the device query by chance 
        self.value_type = ExpectedValueType(compensation_dict.get("value_type", "string"))

        self.symbol = compensation_dict.get("symbol", "")
        self.unit = compensation_dict.get("unit", "")

class CalibrationCapabilities(object): 
    def __init__(self, capabilities_dict):
        # use default of 0.9 second if not defined 
        self.latency = capabilities_dict.get("latency", 0.9) 
        self.start_points = capabilities_dict.get("start_points", [])
        self.points = list(CalibrationCapability(cal) for cal in capabilities_dict.get("points", []))

class CalibrationCapability(object): 
    def __init__(self, capabilities_dict):
        self.id = capabilities_dict.get("id")
        self.description = capabilities_dict.get("description", "")
        self.value_type = ExpectedValueType(capabilities_dict.get("value_type"))
        self.sub_command = capabilities_dict.get("sub_command")
        self.next_points = capabilities_dict.get("next_points", [])

class ConfigurationCapabilities(object): 
    def __init__(self, capabilities_dict):
        parameters = (ConfigurationCapability(p) for p in capabilities_dict)
        self.parameters = {p.parameter:p for p in parameters}

class ConfigurationCapability(object): 
    def __init__(self, capabilities_dict):
        self.parameter = capabilities_dict["parameter"].lower()
        self.description = capabilities_dict["description"]
        self.value_type = ExpectedValueType(capabilities_dict["value_type"])
        self.command = capabilities_dict["command"].lower()
