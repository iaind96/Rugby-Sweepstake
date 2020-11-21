from sweepstake import create_app
from tests.conftest import ConfigTesting


def test_config():
    assert not create_app().testing
    assert create_app(ConfigTesting).testing