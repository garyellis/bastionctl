from bastionctl.cli import cli
from click.testing import CliRunner


class TestCliBastion(object):
    def setup_method(self, test_method):
        self.runner = CliRunner()

    def teardown_method(self, test_method):
        pass

    def test_bastion_help(self):
        pass
        result = self.runner.invoke(
            cli,
            args=['bastion', '--help'])
        assert result.exit_code == 0

    def test_bastion_list(self):
        pass
        result = self.runner.invoke(
            cli,
            args=['bastion', 'list'])
        assert result.exit_code == 0
