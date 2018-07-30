import ec2_patching.utils
import mock


class MockResponse():
    def __init__(self, *args, **kwargs):
        self.status_code = '200'
        self.text = '1.1.1.1'


class TestUtils():
    @mock.patch('ec2_patching.utils.requests.get', side_effect=MockResponse)
    def test_get_public_ip(self, mock_get):
        ip = ec2_patching.utils.get_public_ip()
        assert '/32' in ip
