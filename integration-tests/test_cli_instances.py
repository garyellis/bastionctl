from ec2_patching.cli import cli
from click.testing import CliRunner


class TestCliInstances(object):
    def setup_method(self, test_method):
        self.runner = CliRunner()

    def teardown_method(self, test_method):
        pass

    def test_instances_help(self):
        pass
        result = self.runner.invoke(
            cli,
            args=['instances', '--help'])
        assert result.exit_code == 0

    def test_instances_list(self):
        pass
        result = self.runner.invoke(
            cli,
            args=['instances', 'list'])
        assert result.exit_code == 0
