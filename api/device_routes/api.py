import os
import sys

from flask import request
from flask_restx import Api, Resource

from .models import add_device_models
from .errors import add_device_errors

from atlas_scientific.device import AtlasScientificDeviceBus

def add_device_routes(self, i2cbus):
    device_bus = AtlasScientificDeviceBus(i2cbus)

    device_ns = self.namespace('api/device', description='I2C Device operations')
    models = device_ns.add_device_models()
    device_ns.add_device_errors()

    @device_ns.route('/')
    class DeviceList(Resource):

        @device_ns.marshal_list_with(models.device_info_model)
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

        @device_ns.marshal_list_with(models.device_sample_model)
        def get(self, address):
            device = device_bus.get_device_by_address(address)
            return device.read_sample([]), 200

        @device_ns.marshal_list_with(models.device_sample_model)
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

Api.add_device_routes = add_device_routes