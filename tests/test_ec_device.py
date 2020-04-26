import unittest
from unittest.mock import Mock, call, patch

from atlas_scientific.device import AtlasScientificDeviceBus
from datetime import datetime, timezone
import api

from i2c import I2CBus

class EcDeviceTests(unittest.TestCase):
 
    def setUp(self):
        self.i2cbus = I2CBus()
        self.i2cbus.read = Mock()
        self.i2cbus.write = Mock()
        self.i2cbus.ping = Mock() 
        
        self.app = api.create_app(self.i2cbus).test_client()

    # sample tests

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_ec_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,EC\00',        # second call should be to read the current device outputs
                b'\x011.2\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "EC", "timestamp": "2020-02-25 23:08:13+00:00", "value": "1.2", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_tds_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,TDS\00',        # second call should be to read the current device outputs
                b'\x012000\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "T.D.S.", "timestamp": "2020-02-25 23:08:13+00:00", "value": "2000", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_ms_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,S\00',        # second call should be to read the current device outputs
                b'\x0150000\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "\u03bcS", "timestamp": "2020-02-25 23:08:13+00:00", "value": "50000", "value_type": "float"}]\n', response.data)

    @patch('time.sleep', return_value=None)
    @patch('atlas_scientific.device.get_datetime_now', return_value = datetime.fromtimestamp(1582672093, timezone.utc))
    def test_can_sample_atlas_scientific_ec_device_with_sg_enabled(self, datetime_now_mock, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,SG\00',        # second call should be to read the current device outputs
                b'\x0150000\00'           # third call should be for reading the device sample
            ]

        # Act
        response = self.app.get('/api/device/100/sample', follow_redirects=True)

        # Assert
        self.i2cbus.write.assert_has_calls([
                call(device_address, b'i\00'),   # expect 'i' for read info
                call(device_address, b'o,?\00'), # expect 'o,?' for reading current device output
                call(device_address, b'r\00')    # expect 'r' for read device sample
            ], 
            any_order=False)

        # expect to wait for result to be ready
        patched_time_sleep.assert_has_calls([
                call(0.3), # "i"
                call(0.3), # "o,?"
                call(0.6)  # "r"
            ], 
            any_order=False)

        # expect device info to be read from bus
        self.i2cbus.read.assert_has_calls([
                call(device_address),
                call(device_address),
                call(device_address),
            ], 
            any_order=False)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(b'[{"symbol": "S.G.", "timestamp": "2020-02-25 23:08:13+00:00", "value": "50000", "value_type": "float"}]\n', response.data)

    # sample output tests
    @patch('time.sleep', return_value=None)
    def test_can_resolve_supported_outputs_atlas_scientific_ec_device(self, patched_time_sleep):

        # Arrange
        device_address = 100

        self.i2cbus.read.side_effect = [
                b'\x01?i,EC,2.10\00',   # first call should be for the device info
                b'\x01?O,EC\00',        # second call should be to read the current device outputs
            ]

        # Act
        response = self.app.get('/api/device/100/sample/output', follow_redirects=True)

        # Assert
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

        # expect a empty json list
        self.assertEqual(response.status_code, 200)

        expected_response = '['\
                '{"is_enable": true, "symbol": "EC", "unit": "Conductivity", "value_type": "float"}, ' \
                '{"is_enable": false, "symbol": "T.D.S.", "unit": "Total Dissolved Solids", "value_type": "float"}, ' \
                '{"is_enable": false, "symbol": "\\u03bcS", "unit": "microsiemens", "value_type": "float"}, ' \
                '{"is_enable": false, "symbol": "S.G.", "unit": "Specific Gravity", "value_type": "float"}' \
            ']\n'

        self.assertEqual(expected_response.encode('utf8'), response.data)
        print(response.data.decode('utf-8')) 


if __name__ == '__main__':
    unittest.main()
