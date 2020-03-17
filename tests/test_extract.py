import mock
import unittest
from ignition import extract


class TestIgnitionExtract(unittest.TestCase):

    @mock.patch('os.path.exists', mock.MagicMock(autospec=True, return_value=False))
    def test_is_valid_file_fail(self):
        mock_parser = mock.MagicMock()
        file_path = "/path/not/exists"
        extract.is_valid_file(mock_parser, file_path)
        mock_parser.error.assert_called_once_with('The file %s does not exist!' % file_path)

    @mock.patch('os.makedirs')
    @mock.patch('ignition.extract.open')
    @mock.patch('os.chmod')
    def test_write_files(self, mock_chmod, mock_open, mock_makedirs):
        ignition_files = [{'filesystem': 'root',
                           'path': '/etc/profile.d/proxy.sh',
                           'user': {'name': 'root'},
                           'contents': {'source': 'data:text/plain;charset=utf-8;base64,',
                                        'verification': {}},
                           'mode': 384},
                          {'filesystem': 'root',
                           'path': '/etc/pki/ca-trust/source/anchors/ca.crt',
                           'user': {'name': 'root'},
                           'contents': {'source': 'data:text/plain;charset=utf-8;base64,',
                                        'verification': {}},
                           'mode': 384}
                          ]
        """writes the given files to disk."""
        updater = extract.IgnitionExtract({}, "/host")
        updater.write_files(ignition_files)

        mock_makedirs.assert_has_calls([mock.call('/host/etc/profile.d', exist_ok=True),
                                        mock.call('/host/etc/pki/ca-trust/source/anchors', exist_ok=True)],
                                       any_order=True)
        mock_open.assert_has_calls([mock.call('/host/etc/profile.d/proxy.sh', 'w'),
                                    mock.call('/host/etc/pki/ca-trust/source/anchors/ca.crt', 'w')],
                                   any_order=True)
        mock_chmod.assert_has_calls([mock.call('/host/etc/profile.d/proxy.sh', 384),
                                     mock.call('/host/etc/pki/ca-trust/source/anchors/ca.crt', 384)])

    def test_write_units(self):
        pass

    def test_enable_unit(self):
        pass

    def test_disable_unit(self):
        pass
