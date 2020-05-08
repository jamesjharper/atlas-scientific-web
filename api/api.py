import os
import logging
import sys

from flask import Flask, request
from flask_restx import Api, Resource, marshal
from flask_cors import CORS

from .models import add_device_models
from .errors import add_device_errors

from i2c import I2CBus
from atlas_scientific.device import AtlasScientificDeviceBus

def config_logging():
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def logging_application_banner():
    logging.info('')
    logging.info('========================')
    logging.info('I2C Microserverice start')
    logging.info('========================')
    logging.info('')

def create_app(i2cbus =I2CBus()): 
    config_logging()
    logging_application_banner()

    app = Flask(__name__)
    CORS(app)

    api = Api(app, version='1.0', title='I2C Microserverice',
        description='A description of a microserverice',
    )
    device_ns = api.namespace('api/device', description='I2C Device operations')

    device_bus = AtlasScientificDeviceBus(i2cbus)
    
    models = device_ns.add_device_models()
    device_ns.add_device_errors()

    @app.before_request
    def log_request_info():
        app.logger.debug('\n[%s] %s\nBody:\n%s', request.method , request.path, request.get_data())

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def index(path):

        bg_lookup = {
            'pH': 'bg-success',
            'ORP': 'bg-info',
            'DO': 'bg-warning',
            'EC': 'bg-success',
        }

        device_elements = []
        for device in device_bus.get_known_devices():
            device_sample = device.read_sample([])
            device_type = device.get_device_info().device_type;
            device_colour = bg_lookup[device_type]

            sample_value = ' / '.join(f"{sample.value} {sample.symbol}" for sample in device_sample)
            device_elements.append(f'<div class="p-3 mb-2 {device_colour} text-white"><h1>{device_type} : {sample_value}</h1></div>')


        return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <title>Water quality Probes</title>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <meta http-equiv="refresh" content="10">
                <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/css/bootstrap.min.css">
                <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
                <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.16.0/umd/popper.min.js"></script>
                <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.4.1/js/bootstrap.min.js"></script>
            </head>
            <body>
                {''.join(device_elements)}
            </body>
            </html>
        """

    @device_ns.route('/')
    class DeviceList(Resource):

        @device_ns.marshal_list_with(models.device_info)
        def get(self):
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

        @device_ns.marshal_list_with(models.device_sample)
        def get(self, address):
            device = device_bus.get_device_by_address(address)
            return device.read_sample([]), 200

        @device_ns.marshal_list_with(models.device_sample)
        @device_ns.expect(models.device_sample_compensation)
        def post(self, address):
            device = device_bus.get_device_by_address(address)
            compensation_factors = models.device_compensation_factors_schema.load_request(request)
            return device.read_sample(compensation_factors), 200

    @device_ns.route('/<int:address>/sample/output')
    class DeviceSampleOutput(Resource):
        @device_ns.marshal_list_with(models.device_sample_output)
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

        @device_ns.expect(models.set_device_sample_outputs)
        def post(self, address):
            device = device_bus.get_device_by_address(address)
            device.set_enabled_output_measurements(request.json)
            return '', 200

    @device_ns.route('/<int:address>/sample/compensation')
    class DeviceSampleCompensation(Resource):

        @device_ns.expect(models.device_sample_compensation)
        def post(self, address):
            compensation_factors = models.device_compensation_factors_schema.load_request(request)
            device = device_bus.get_device_by_address(address)
            device.set_measurement_compensation_factors(compensation_factors)

            return '', 200

    @device_ns.route('/<int:address>/sample/calibration')
    class DeviceSampleCalibration(Resource):

        @device_ns.expect(models.device_sample_calibration)
        def put(self, address):
            calibration_point = models.device_calibration_point_schema.load_request(request)
            device = device_bus.get_device_by_address(address)
            device.set_calibration_point(calibration_point)

            return '', 200

    @device_ns.route('/<int:address>/configuration')
    class DeviceConfiguration(Resource):

        @device_ns.expect(models.device_configuration_parameter)
        def post(self, address):
            configuration_parameter = models.device_configuration_parameter_schema.load_request(request)
            device = device_bus.get_device_by_address(address)
            device.set_configuration_parameter(configuration_parameter)

            return '', 200

    

    return app