import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api

from i2c import I2CBusIo

class OrpDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBusIo()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = api.create_app(self.i2cbus).test_client()
 

    # Sample tests

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_orp_device(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 98

        self.i2cbus.read.side_effect = [ 
                b'\x01?I,ORP,1.97\00', # first call should be for the device info
                b'\x01209.6\00'  # second call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/98/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
                call(device_address, b'r\00')  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.9)  
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)  
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "mV", "timestamp": "2020-02-25 23:08:13+00:00", "value": "209.6", "value_type": "float", "unit_code": "ORP"}]\n', response.data)

    # Sample output tests

    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_orp_device(self, patched_time_sleep):

        # Arrange
        device_address = 98

        self.i2cbus.read.side_effect = [
                b'\x01?I,ORP,1.97\00', # first call should be for the device info
            ]

        # Act
        response = self.app.get('/api/device/98/sample/output', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'), # expect 'i' for read info
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3)
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"is_enable": true, "symbol": "mV", "unit": "Oxidation Reduction Potential", "unit_code": "ORP", "value_type": "float"}]\n', response.data)

    # compensation tests

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_should_return_invalid_request_when_sampling_atlas_scientific_orp_device_with_temperature_compensation(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [ 
                b'\x01?I,ORP,1.97\00', # first call should be for the device info
            ]

        # Act
        request_body = [{
            'factor': 'temperature',
            'symbol': '°C', 
            'value': '25.5'
        }]

        # Act
        response = self.app.post('/api/device/98/sample', json=request_body, follow_redirects=True)

        # Assert
        self.assertEqual(response.status_code, 400)
        self.assertEqual(b'{"message": "Request contains a missing or incorrectly formatted felid.", "error_code": "INVALID_REQUEST_ERROR"}\n', response.data)

    # configuration tests

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_name_in_atlas_scientific_orp_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,ORP,1.98\00', # first call should be for the device info
                b'\x01\00',           # second call should be to read the result from setting the device name
            ]

        # Act
        request_body = {
            'parameter': 'name',
            'value': 'orp_device'
        }

        response = self.app.post(f'/api/device/{device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),              # expect 'i' for read info
                call(device_address, b'name,orp_device\00'), # expect 'name,orp_device' for setting the device name
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "name,orp_device"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_leds_in_atlas_scientific_orp_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
                b'\x01?i,ORP,1.98\00', # first call should be for the device info
                b'\x01\00',           # second call should be to read the result from setting the device name
            ]

        # Act
        request_body = {
            'parameter': 'led',
            'value': 'false'
        }

        response = self.app.post(f'/api/device/{device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'l,0\00'), # expect 'l,1' for setting the device name
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "l,1"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)

    # Calibration tests

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_any_point_in_atlas_scientific_orp_device(self, patched_time_sleep):

        # Arrange
        device_address = 99

        self.i2cbus.read.side_effect = [
            b'\x01?i,ORP,1.98\00', # first call should be for the device info
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'any',
            'actual_value': '225'
        }

        response = self.app.put('/api/device/99/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'Cal,225\00'), # expect 'Cal,225' for setting the calibration point
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.9), # "Cal,225"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address), 
                call(device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

        
