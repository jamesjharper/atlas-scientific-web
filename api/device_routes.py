import os
import logging
import sys

from flask import Flask
from flask_restx import Api, Resource, fields

from flask import jsonify, json, request

from atlas_scientific.models import *
from atlas_scientific.device import AtlasScientificDevice, AtlasScientificDeviceBus

def add_device_routes(self, i2cbus):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    device_bus = AtlasScientificDeviceBus(i2cbus)
    api_log = logging.getLogger(f'API')

    device_ns = self.namespace('api/device', description='I2C Device operations')

    device_error_model = self.model('device_error', {
        'message': fields.String(
            description='A description of the error encountered',
            example='This is your error message'
        ),
        'error_code': fields.String(
            description='The error code of the error encountered',
            example='DEVICE_NOT_READY'
        ),
    })

    device_info_model = self.model('device_info', {
        'address': fields.Integer(
            description='The I2C address of the device.',
            example='97'
        ),
        'device_type': fields.String(
            description='The model of the device detected',
            example='DO'
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

    device_sample_model = self.model('device_sample', {
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

    device_sample_output = self.model('device_sample_output', {
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

    set_device_sample_outputs = self.model('set_device_sample_output', {
        'name': fields.String,
        'members': fields.List(
            fields.String(
                description='Unit to set as the devices sample output.',
                example="Mg"
            )
        ),
    })

    device_sample_compensation = self.model('device_sample_compensation', {
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

    device_sample_calibration = self.model('device_sample_calibration', {
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

    @device_ns.errorhandler(AtlasScientificNotYetSupported)
    @device_ns.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_response_syntax_error(error):
        return {
            'error_code': 'UNSUPPORTED_DEVICE', 
            'message': 'Detected unsupported atlas scientific device.'
        }, 400

    @device_ns.errorhandler(AtlasScientificResponseSyntaxError)
    @device_ns.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_response_syntax_error(error):
        return {
            'error_code': 'UNEXPECTED_DEVICE_RESPONSE', 
            'message': 'Device responded but response was not recognizable.'
        }, 400

    @device_ns.errorhandler(AtlasScientificNoDeviceAtAddress)
    @device_ns.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_no_device_at_address_error(error):
        return {
            'error_code': 'DEVICE_NOT_FOUND', 
            'message': 'No device is connected to the given address.'
        }, 400

    @device_ns.errorhandler(AtlasScientificDeviceNotReadyError)
    @device_ns.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_device_not_ready_error(error):
        return {
            'error_code': 'DEVICE_NOT_READY', 
            'message': 'Device did not return the expected response in a timely mannor.'
        }, 400
   
    @device_ns.errorhandler(AtlasScientificSyntaxError)
    @device_ns.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_syntax_error(error):
        return {
            'error_code': 'COMMAND_ERROR', 
            'message': 'Device has rejected your request, please confrim the request is supported by the device and the device has the latest firmware.'
        }, 400

    @device_ns.errorhandler(AtlasScientificError)
    @device_ns.marshal_with(device_error_model, code=500)
    def handle_atlas_scientific_errors(error):
        return {
            'error_code': 'UNKNOWN', 
            'message': 'Unexpected error was encountered'
        }, 500

    @device_ns.errorhandler(Exception)
    @device_ns.marshal_with(device_error_model, code=500)
    def handle_atlas_scientific_errors(error):
        return {
            'error_code': 'UNEXPECTED_ERROR', 
            'message': 'Unexpected internal error occurred.'
        }, 500

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
            return device.read_sample([]), 200

        @device_ns.marshal_list_with(device_sample_model)
        @device_ns.expect(device_sample_compensation)
        def post(self, address):
            device = device_bus.get_device_by_address(address)
            compensation_factors = (AtlasScientificDeviceCompensationFactor(json_list_item) for json_list_item in request.json)  
            return device.read_sample(compensation_factors), 200
    

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

Api.add_device_routes = add_device_routes