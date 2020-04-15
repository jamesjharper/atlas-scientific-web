import flask
import os
import logging
import sys

from flask import jsonify, json, request
from i2c import I2CBus
from atlas_scientific.models import RequestResult, AtlasScientificResponse, AtlasScientificDeviceCompensationFactor
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

    app = flask.Flask(__name__)
    device_bus = AtlasScientificDeviceBus(i2cbus)
    api_log = logging.getLogger(f'API')

  # TODO: add test for injection
  # TODO: add application token like auth?

    @app.route('/api/device', methods=['GET'])
    def devices():
        api_log.info("[GET]: /api/device")
        device_bus.scan_for_devices()
        i2c_devices = []
        for device in device_bus.get_known_devices():
            device_info = device.get_device_info()
            i2c_devices.append({
                'device_type': device_info.device_type,
                'version': device_info.version,
                'address': device_info.address,
                'vendor': device_info.vendor,
            })
        
        return app.response_class(
            response=json.dumps(i2c_devices),
            status=200,
            mimetype='application/json'
        )

    @app.route('/api/device/<address>/sample', methods=['GET'])
    def device_sample(address):
        api_log.info(f"[GET]: /api/device/{address}/sample")
        device = device_bus.get_device_by_address(int(address))

        result = device.read_sample([])
    
        return app.response_class(
            response=get_json(result),
            status=200,
            mimetype='application/json'
        )

    @app.route('/api/device/<address>/sample', methods=['POST'])
    def device_sample_with_compensation_factor(address):
        api_log.info(f"[POST]: /api/device/{address}/sample")
        api_log.debug(f"Body: {request.json}")
        device = device_bus.get_device_by_address(int(address))

        compensation_factors = (AtlasScientificDeviceCompensationFactor(json_list_item) for json_list_item in request.json)  
        result = device.read_sample(compensation_factors)

        return app.response_class(
            response=get_json(result),
            status=200,
            mimetype='application/json'
        )
    
    @app.route('/api/device/<address>/sample/output', methods=['POST'])
    def set_enabled_output_measurements(address):
        api_log.info(f"[POST]: /api/device/{address}/sample/output")
        api_log.debug(f"Body: {request.json}")

        device = device_bus.get_device_by_address(int(address))
        device.set_enabled_output_measurements(request.json)

        return app.response_class(
            # TODO: create Ok response
            status=200,
            mimetype='application/json'
        )

    @app.route('/api/device/<address>/sample/output', methods=['GET'])
    def get_enabled_output_measurements(address):
        api_log.info(f"[GET]: /api/device/{address}/sample/output")

        device = device_bus.get_device_by_address(int(address))
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
        
        return app.response_class(
            response=json.dumps(sample_outputs),
            status=200,
            mimetype='application/json'
        )

    @app.route('/api/device/<address>/sample/compensation', methods=['POST'])
    def set_measurement_compensation_factor(address):
        api_log.info(f"[POST]: /api/device/{address}/sample/compensation")
        api_log.debug(f"Body: {request.json}")

        device = device_bus.get_device_by_address(int(address))

        compensation_factors = (AtlasScientificDeviceCompensationFactor(json_list_item) for json_list_item in request.json)   
        device.set_measurement_compensation_factors(compensation_factors)

        return app.response_class(
            # TODO: create Ok response
            status=200,
            mimetype='application/json'
        )

    return app