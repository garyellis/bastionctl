from ec2_patching import __version__
from ec2_patching.cli import cli
from click.testing import CliRunner


class TestCli(object):
    def setup_method(self, test_method):
        self.runner = CliRunner()

    def test_vpc_help(self):
        result = self.runner.invoke(
            cli,
            args=['--version']
        )
        assert result.output.rstrip() == __version__
