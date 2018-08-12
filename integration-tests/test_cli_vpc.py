from bastionctl.cli import cli
from click.testing import CliRunner


class TestCliVpc(object):
    def setup_method(self, test_method):
        self.runner = CliRunner()

    def teardown_method(self, test_method):
        pass

    def test_vpc_help(self):
        pass
        result = self.runner.invoke(
            cli,
            args=['vpc', '--help'])
        assert result.exit_code == 0

    def test_vpc_list(self):
        pass
        result = self.runner.invoke(
            cli,
            args=['vpc', 'list'])
        assert result.exit_code == 0
