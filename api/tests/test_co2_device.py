import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api

from i2c import I2CBus

class Co2DeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.device_address = 105
        self.i2cbus = I2CBus()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = api.create_app(self.i2cbus).test_client()
 

    # Sample tests

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_co2_device_with_ppm_output_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [ 
                b'\x01?I,CO2,1.00\00',  # first call should be for the device info
                b'\x01?O,ppm\00',        # second call should be to read the current device outputs
                b'\x01800\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get(f'/api/device/{self.device_address}/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'), # expect 'i' for read info
                call(self.device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(self.device_address, b'r\00')  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.3), 
                call(0.9)  
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address), 
                call(self.device_address), 
                call(self.device_address)  
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "ppm", "timestamp": "2020-02-25 23:08:13+00:00", "value": "800", "value_type": "int"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_co2_device_with_device_temperature_output_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [ 
                b'\x01?I,CO2,1.00\00',  # first call should be for the device info
                b'\x01?O,t\00',        # second call should be to read the current device outputs
                b'\x0130.1\00'         # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get(f'/api/device/{self.device_address}/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'), # expect 'i' for read info
                call(self.device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(self.device_address, b'r\00')  # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), 
                call(0.3), 
                call(0.9)  
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address), 
                call(self.device_address), 
                call(self.device_address)  
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "\\u00b0C", "timestamp": "2020-02-25 23:08:13+00:00", "value": "30.1", "value_type": "float"}]\n', response.data)


    # Sample output tests

    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_co2_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
                b'\x01?I,CO2,1.00\00', # first call should be for the device info
                b'\x01?O,ppm,t\00',    # second call should be to read the current device outputs
            ]

        # Act
        response = self.app.get(f'/api/device/{self.device_address}/sample/output', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'), # expect 'i' for read info
                call(self.device_address, b'o,?\00'), # expect 'o,?' for reading current device output
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3),
                call(0.3)
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address), 
                call(self.device_address), 
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        expected_response = '['\
                '{"is_enable": true, "symbol": "ppm", "unit": "Gaseous CO2", "value_type": "int"}, ' \
                '{"is_enable": true, "symbol": "\\u00b0C", "unit": "Internal device temperature", "value_type": "float"}' \
            ']\n'

        self.assertEqual(expected_response.encode('utf8'), response.data)


    @patch('time.sleep', return_value=None)
    def test_can_enable_internal_temperature_output_on_atlas_scientific_co2_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
                b'\x01?I,CO2,1.00\00', # first call should be for the device info
                b'\x01?O,ppm\00',      # second call should be to read the current device outputs
                b'\x01\00',             # call should be to read the result from adding t to device output
                b'\x01\00',             # call should be to read the result from removing ppm device output
            ]

        # Act
        # body should be a list of all the units to be enabled.
        # Note, all other units not in this list will be disabled 
        request_body = ['T']

        # Act
        enable_t_response = self.app.post(f'/api/device/{self.device_address}/sample/output', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'),          # expect 'i' for read info
                call(self.device_address, b'o,?\00'),        # expect 'o,?' for reading current device output
                call(self.device_address, b'o,T,1\00'),      # expect 'o,t,1
                call(self.device_address, b'o,PPM,0\00'),    # expect 'o,ppm,0
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.3), # "o,t,1"
                call(0.3), # "o,ppm,0"
            ], 
            any_order=False)
        
        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(self.device_address), 
                call(self.device_address), 
                call(self.device_address), 
                call(self.device_address),
            ], 
            any_order=False)

        self.assertEqual(enable_t_response.status_code, 200)


    # configuration tests

    @patch('time.sleep', return_value=None)
    def test_can_configure_device_name_in_atlas_scientific_co2_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
                b'\x01?i,CO2,1.00\00', # first call should be for the device info
                b'\x01\00',           # second call should be to read the result from setting the device name
            ]

        # Act
        request_body = {
            'parameter': 'name',
            'value': 'co2_device'
        }

        response = self.app.post(f'/api/device/{self.device_address}/configuration', json=request_body, follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(self.device_address, b'i\00'),              # expect 'i' for read info
                call(self.device_address, b'name,co2_device\00'), # expect 'name,co2_device' for setting the device name
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "name,co2_device"
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
    def test_can_configure_device_leds_in_atlas_scientific_co2_device(self, patched_time_sleep):

        # Arrange
        self.i2cbus.read.side_effect = [
                b'\x01?i,CO2,1.00\00', # first call should be for the device info
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
        
