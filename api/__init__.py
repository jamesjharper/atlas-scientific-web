
import os
import logging
import sys

from flask import Flask
from flask_restx import Api, Resource, fields

from flask import jsonify, json, request
from i2c import I2CBus
from atlas_scientific.models import RequestResult, AtlasScientificResponse, AtlasScientificDeviceCompensationFactor, AtlasScientificDeviceCalibrationPoint
from atlas_scientific.device import AtlasScientificDevice, AtlasScientificDeviceBus
i2cbus = I2CBus()



def config_logging():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def logging_application_banner():
    logging.info('')
    logging.info('========================')
    logging.info('I2C Microserverice start')
    logging.info('========================')
    logging.info('')

def get_json(object):
    return json.dumps(object, default=lambda o: getattr(o, '__dict__', str(o)))

def create_app(): 
    config_logging()
    logging_application_banner()

    app = Flask(__name__)
    api = Api(app, version='1.0', title='I2C Microserverice',
        description='A description of a microserverice',
    )

    device_bus = AtlasScientificDeviceBus(i2cbus)
    api_log = logging.getLogger(f'API')

    device_ns = api.namespace('api/device', description='I2C Device operations')

    device_info_model = api.model('device_info', {
        'address': fields.Integer(
            description='The I2C address of the device.',
            example='97'
        ),
        'device_type': fields.String(
            description='The model of the device detected',
            example='D.O.'
        ),
        'vendor': fields.String(
            description='The manifactor of the device',
            example='atlas-scientific'
        ),
        'firmware_version': fields.String(
            description='The firmware version of the detected device',
            example='1.98'
        ), 
    })

    device_sample_model = api.model('device_sample', {
        'symbol': fields.String(
            description='The samples unit of measurement.',
            example='mg/L'
        ),
        'timestamp': fields.String(
            description='The moment in which the sample was record. Should always be returned in UTC.',
            example='2020-02-25 23:08:13+00:00'
        ),
        'value': fields.String(
            description='The sample recorded. Alway represented as a string.',
            example='238.1'
        ), 
        'value_type': fields.String(
            description='Data type of the recorded sample.',
            example='float'
        ), 
    })

    device_sample_output = api.model('device_sample_output', {
        'is_enable': fields.Boolean(
            description='The current enable state of the device output. True indicates the output will be reported when the device is sampled',
            example=True
        ),
        'symbol': fields.String(
            description='The symbol of the unit of measurement reported by this sample output.',
            example='pH'
        ),
        'unit': fields.String(
            description='The the unit of measurement reported by this sample output.',
            example='Percent saturation'
        ), 
        'value_type': fields.String(
            description='Data type of the sample reported by this sample output..',
            example='float'
        ), 
    })

    set_device_sample_outputs = api.model('set_device_sample_output', {
        'name': fields.String,
        'members': fields.List(
            fields.String(
                description='Unit to set as the devices sample output.',
                example="Mg"
            )
        ),
    })

    device_sample_compensation = api.model('device_sample_compensation', {
        'factor': fields.String(
            description='The measurement factor to compensate for.',
            example="pressure"
        ),
        'symbol': fields.String(
            description='The symbol of the unit of measurement compensation used by when sampling.',
            example='kPa'
        ),
        'value': fields.String(
            description='The known value of the measurement compensation. Alway represented as a string.',
            example='90.25'
        ), 
    })

    device_sample_calibration = api.model('device_sample_calibration', {
        'point': fields.String(
            description='The calibration point to set',
            example="mid"
        ),
        'actual_value': fields.String(
            description='The known value of the expected measurement. Alway represented as a string.',
            example='90.25'
        ), 
    })


   # TODO: add test for injection
   # TODO: add application token like auth?

    @app.before_request
    def log_request_info():
        app.logger.debug('\n[%s] %s\nBody:\n%s', request.method , request.path, request.get_data())

    @device_ns.route('/')
    class DeviceList(Resource):

        @device_ns.marshal_list_with(device_info_model)
        def get(self):
            api_log.info("[GET]: /api/device")
            device_bus.scan_for_devices()
            i2c_devices = []
            for device in device_bus.get_known_devices():
                device_info = device.get_device_info()
                i2c_devices.append({
                    'device_type': device_info.device_type,
                    'firmware_version': device_info.version,
                    'address': device_info.address,
                    'vendor': device_info.vendor,
                })
            
            return i2c_devices
            

    @device_ns.route('/<int:address>/sample')
    @device_ns.doc(params={'address': 'An I2C Address of a device'})
    class DeviceSample(Resource):

        @device_ns.marshal_list_with(device_sample_model)
        def get(self, address):
            device = device_bus.get_device_by_address(address)
            return device.read_sample([])

        @device_ns.marshal_list_with(device_sample_model)
        @device_ns.expect(device_sample_compensation)
        def post(self, address):
            device = device_bus.get_device_by_address(int(address))
            compensation_factors = (AtlasScientificDeviceCompensationFactor(json_list_item) for json_list_item in request.json)  
            return device.read_sample(compensation_factors)
    

    @device_ns.route('/<int:address>/sample/output')
    class DeviceSampleOutput(Resource):
        @device_ns.marshal_list_with(device_sample_output)
        def get(self, address):
            device = device_bus.get_device_by_address(address)
            supported_outputs = device.get_supported_output_measurements()
            enabled_outputs = set(m.unit_code for m in device.get_enabled_output_measurements())

            sample_outputs = []
            for sample_output in supported_outputs:
                sample_outputs.append({
                    'symbol': sample_output.symbol,
                    'unit': sample_output.unit,
                    'value_type': sample_output.value_type,
                    'is_enable': sample_output.unit_code in enabled_outputs
                })
            
            return sample_outputs

        @device_ns.expect(set_device_sample_outputs)
        def post(self, address):
            device = device_bus.get_device_by_address(address)
            device.set_enabled_output_measurements(request.json)
            return '', 200

    @device_ns.route('/<int:address>/sample/compensation')
    class DeviceSampleCompensation(Resource):

        @device_ns.expect(device_sample_compensation)
        def post(self, address):
            device = device_bus.get_device_by_address(address)

            compensation_factors = (AtlasScientificDeviceCompensationFactor(json_list_item) for json_list_item in request.json)   
            device.set_measurement_compensation_factors(compensation_factors)

            return '', 200

    @device_ns.route('/<int:address>/sample/calibration')
    class DeviceSampleCalibration(Resource):

        @device_ns.expect(device_sample_calibration)
        def put(self, address):
            device = device_bus.get_device_by_address(address)

            calibration_point = AtlasScientificDeviceCalibrationPoint(request.json)   
            device.set_calibration_point(calibration_point)

            return '', 200

    return app