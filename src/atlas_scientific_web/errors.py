import logging

from flask_restx import Namespace, Resource, fields
from marshmallow import ValidationError, Schema, post_load, fields as m_fields

from .hardware.models import RequestValidationError, \
    AtlasScientificDeviceNotYetSupported, \
    AtlasScientificResponseSyntaxError, \
    AtlasScientificNoDeviceAtAddress, \
    AtlasScientificDeviceNotReadyError, \
    AtlasScientificSyntaxError, \
    AtlasScientificError

def add_device_errors(self):
    devices_api_log = logging.getLogger(f'DeviceApiErrors')

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

    def load_request(self, request):
        try:
            return self.load(request.json)
        except ValidationError as err:
            # make sure we don't leak any validation logic to the consumer
            devices_api_log.error(f"Input validation error {err.normalized_messages()}")
            raise RequestValidationError()
    Schema.load_request = load_request

    @self.errorhandler(RequestValidationError)
    @self.marshal_with(device_error_model, code=400)
    def handle_request_validation_error(error):
        return {
            'error_code': 'INVALID_REQUEST_ERROR', 
            'message': "Request contains a missing or incorrectly formatted felid."
        }, 400

    @self.errorhandler(AtlasScientificDeviceNotYetSupported)
    @self.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_response_syntax_error(error):
        return {
            'error_code': 'UNSUPPORTED_DEVICE', 
            'message': 'Detected unsupported atlas scientific device.'
        }, 400

    @self.errorhandler(AtlasScientificResponseSyntaxError)
    @self.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_response_syntax_error(error):
        return {
            'error_code': 'UNEXPECTED_DEVICE_RESPONSE', 
            'message': 'Device responded but response was not recognizable.'
        }, 400

    @self.errorhandler(AtlasScientificNoDeviceAtAddress)
    @self.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_no_device_at_address_error(error):
        return {
            'error_code': 'DEVICE_NOT_FOUND', 
            'message': 'No device is connected to the given address.'
        }, 400

    @self.errorhandler(AtlasScientificDeviceNotReadyError)
    @self.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_device_not_ready_error(error):
        return {
            'error_code': 'DEVICE_NOT_READY', 
            'message': 'Device did not return the expected response in a timely mannor.'
        }, 400
   
    @self.errorhandler(AtlasScientificSyntaxError)
    @self.marshal_with(device_error_model, code=400)
    def handle_atlas_scientific_syntax_error(error):
        return {
            'error_code': 'COMMAND_ERROR', 
            'message': 'Device has rejected your request, please confrim the request is supported by the device and the device has the latest firmware.'
        }, 400

    @self.errorhandler(AtlasScientificError)
    @self.marshal_with(device_error_model, code=500)
    def handle_atlas_scientific_errors(error):
        return {
            'error_code': 'UNKNOWN_ERROR', 
            'message': 'Unexpected error was encountered'
        }, 500

    @self.errorhandler(Exception)
    @self.marshal_with(device_error_model, code=500)
    def handle_atlas_scientific_errors(error):
        return {
            'error_code': 'UNEXPECTED_ERROR', 
            'message': 'Unexpected internal error occurred.'
        }, 500

Namespace.add_device_errors = add_device_errors