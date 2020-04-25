import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api

from i2c import I2CBus

class AnyDeviceErrorTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBus()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = api.create_app(self.i2cbus).test_client()

    def test_should_return_expected_value_missing_error_when_compensation_factor_missing(self):
        # Arrange
        request_body = [{
            #'factor': 'salinity',
            'symbol': 'μS', 
            'value': '50000'
        }]

        # Act
        response = self.app.post('/api/device/97/sample/compensation', json=request_body, follow_redirects=True)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'{"message": "Request contains a missing or incorrectly formatted felid.", "error_code": "INVALID_REQUEST_ERROR"}\n', response.data)

if __name__ == '__main__':
    unittest.main()
