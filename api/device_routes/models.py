from flask_restx import Api, Resource, fields, Namespace
from marshmallow import ValidationError, Schema, post_load, fields as m_fields
from atlas_scientific.models import AtlasScientificDeviceCompensationFactor, AtlasScientificDeviceCalibrationPoint

class DeviceModels(object):
    pass

def add_device_models(self):

    m = DeviceModels()
    m.device_info_model = self.model('device_info', {
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

    m.device_sample_model = self.model('device_sample', {
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

    m.device_sample_output = self.model('device_sample_output', {
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

    m.set_device_sample_outputs = self.model('set_device_sample_output', {
        'name': fields.String,
        'members': fields.List(
            fields.String(
                description='Unit to set as the devices sample output.',
                example="Mg"
            )
        ),
    })

    m.device_sample_calibration = self.model('device_sample_calibration', {
        'point': fields.String(
            description='The calibration point to set',
            example="mid",
            required=True
        ),
        'actual_value': fields.String(
            description='The known value of the expected measurement. Alway represented as a string.',
            example='90.25',
            required=True
        ), 
    })

    class AtlasScientificDeviceCalibrationPointSchema(Schema):
        point = m_fields.Str(missing=None, required=False)
        actual_value = m_fields.Str(required=True)

        @post_load
        def make(self, data, **kwargs):
            return AtlasScientificDeviceCalibrationPoint(**data)

    m.device_calibration_point_schema = AtlasScientificDeviceCalibrationPointSchema()

    m.device_sample_compensation = self.model('device_sample_compensation', {
        'factor': fields.String(
            description='The measurement factor to compensate for.',
            example="pressure",
            required=True
        ),
        'symbol': fields.String(
            description='The symbol of the unit of measurement compensation used by when sampling.',
            example='kPa',
            required=True
        ),
        'value': fields.String(
            description='The known value of the measurement compensation. Alway represented as a string.',
            example='90.25',
            required=True
        ), 
    })

    class AtlasScientificDeviceCompensationFactorSchema(Schema):
        factor = m_fields.Str(required=True)
        symbol = m_fields.Str(required=True)
        value = m_fields.Str(required=True)

        @post_load
        def make(self, data, **kwargs):
            return AtlasScientificDeviceCompensationFactor(**data)
        
    m.device_compensation_factors_schema = AtlasScientificDeviceCompensationFactorSchema(many=True)
    return m

Namespace.add_device_models = add_device_models