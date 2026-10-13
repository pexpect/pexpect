"""Environment validation must happen before a child is forked."""
import subprocess
import sys
from unittest import mock

import pytest

import pexpect


@pytest.mark.skipif(sys.version_info[0] < 3, reason="Python 3 environment types")
@pytest.mark.parametrize("env", [
    {"BLAH": 1},
    {1: "value"},
    {"BLAH": None},
    {"BLAH": 1.5},
    {"PATH": 1},
])
def test_invalid_environment_rejected_before_spawn(env):
    with mock.patch.object(pexpect.spawn, "_spawnpty", side_effect=AssertionError(
            "Invalid environment reached the fork boundary")) as spawnpty:
        with pytest.raises(TypeError):
            pexpect.spawn(sys.executable, ["-c", "pass"], env=env)
        spawnpty.assert_not_called()


def test_invalid_environment_raises_in_parent():
    code = """
import pexpect
try:
    child = pexpect.spawn('/usr/bin/env', env={'BLAH': 1})
except TypeError:
    print('rejected in parent')
else:
    child.expect(pexpect.EOF)
    child.close()
    raise AssertionError('invalid environment was accepted')
"""
    result = subprocess.run([sys.executable, "-c", code],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            timeout=5)
    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == b"rejected in parent"


@pytest.mark.parametrize("env", [
    {"BLAH": "value"},
    {b"BLAH": b"value"},
    {"BLAH": "caf\u00e9"},
    {},
    None,
])
def test_valid_environment_preserved(env):
    original = None if env is None else env.copy()
    with pexpect.spawn(sys.executable, ["-c", "import os; print(repr(os.environ.get('BLAH')))"],
                       env=env, encoding="utf-8", timeout=5) as child:
        child.expect(pexpect.EOF)
        child.wait()
        assert child.exitstatus == 0
        if env:
            expected = env.get("BLAH", env.get(b"BLAH"))
            if isinstance(expected, bytes):
                expected = expected.decode("utf-8")
            assert repr(expected) in child.before
    assert env == original


@pytest.mark.skipif(sys.version_info[0] < 3, reason="PathLike requires Python 3")
def test_pathlike_environment_preserved():
    class EnvValue(object):
        def __fspath__(self):
            return "value"

    with pexpect.spawn(sys.executable, ["-c", "import os; print(os.environ['BLAH'])"],
                       env={"BLAH": EnvValue()}, encoding="utf-8", timeout=5) as child:
        child.expect(pexpect.EOF)
        child.wait()
        assert child.exitstatus == 0
        assert child.before.strip() == "value"
