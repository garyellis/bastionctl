import bastionctl.utils
import mock


class MockResponse():
    def __init__(self, *args, **kwargs):
        self.status_code = '200'
        self.text = '1.1.1.1'


class TestUtils():
    @mock.patch('bastionctl.utils.requests.get', side_effect=MockResponse)
    def test_get_public_ip(self, mock_get):
        ip = bastionctl.utils.get_public_ip()
        assert '/32' in ip
