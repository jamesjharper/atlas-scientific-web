import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api

from i2c import I2CBusIo

class RtdDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.device_address = 102
        self.i2cbus = I2CBusIo()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = api.create_app(self.i2cbus).test_client()
 

    # Sample tests

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_rtd_device(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [ 
                b'\x01?I,RTD,2.01\00',  # first call should be for the device info
                b'\x0125.104\00'        #  call should be for reading the device sample
            ]

        # Act
        response = self.app.get(f'/api/device/{self.device_address}/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'), # expect 'i' for read info
                call(self.device_address, b'r\00')  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.6)  
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address),
                call(self.device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "\\u00b0", "timestamp": "2020-02-25 23:08:13+00:00", "value": "25.104", "value_type": "float"}]\n', response.data)


    # Sample output tests

    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_rtd_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
                b'\x01?I,RTD,2.01\00',  # first call should be for the device info
            ]

        # Act
        response = self.app.get(f'/api/device/{self.device_address}/sample/output', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'), # expect 'i' for read info
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3),
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address), 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        expected_response = '['\
                '{"is_enable": true, "symbol": "\\u00b0", "unit": "Temperature", "value_type": "float"}' \
            ']\n'

        self.assertEqual(expected_response.encode('utf8'), response.data)

    # configuration tests

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_name_in_atlas_scientific_rtd_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
                b'\x01?I,RTD,2.01\00',  # first call should be for the device info
                b'\x01\00',           # second call should be to read the result from setting the device name
            ]

        # Act
        request_body = {
            'parameter': 'name',
            'value': 'rtd_device'
        }

        response = self.app.post(f'/api/device/{self.device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'),              # expect 'i' for read info
                call(self.device_address, b'name,rtd_device\00'), # expect 'name,rtd_device' for setting the device name
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "name,rtd_device"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address), 
                call(self.device_address)
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_leds_in_atlas_scientific_rtd_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
                b'\x01?I,RTD,2.01\00',  # first call should be for the device info
                b'\x01\00',           # second call should be to read the result from setting the device name
            ]

        # Act
        request_body = {
            'parameter': 'led',
            'value': 'false'
        }

        response = self.app.post(f'/api/device/{self.device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'),   # expect 'i' for read info
                call(self.device_address, b'l,0\00'), # expect 'l,1' for setting the device name
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
                call(self.device_address), 
                call(self.device_address)
            ], 
            any_order=False)

        # expect a empty json list 
        self.assertEqual(response.status_code, 200)
        

    # TODO: Add tests for setting scale setting

    # Calibration tests

    @patch('time.sleep', return_value=None)
    def test_can_calibrate_any_point_in_atlas_scientific_rtd_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
            b'\x01?I,RTD,2.01\00',  # first call should be for the device info
            b'\x01\00',            # call should be to read the result from setting the calibration point
        ]

        request_body = {
            'point': 'any',
            'actual_value': '100.0'
        }

        response = self.app.put(f'/api/device/{self.device_address}/sample/calibration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'),         # expect 'i' for read info
                call(self.device_address, b'Cal,100.0\00'), # expect 'Cal,100.0' for setting the calibration point
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.6), # "Cal,100"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address), 
                call(self.device_address)
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)

        