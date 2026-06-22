"""Tests for the test-runner helpers in utilities/testing.py."""

from types import SimpleNamespace

from utilities import testing


def _fake_run(returncode=0, recorder=None):
    def _run(cmd, *args, **kwargs):
        if recorder is not None:
            recorder["cmd"] = cmd
            recorder["cwd"] = kwargs.get("cwd")
        return SimpleNamespace(returncode=returncode)

    return _run


def test_run_pytest_invokes_uv(mocker):
    recorder = {}
    mocker.patch.object(testing.subprocess, "run", _fake_run(0, recorder))
    assert testing.run_pytest() == 0
    assert recorder["cmd"] == ["uv", "run", "pytest"]


def test_run_integration_dispatches_test_action(mocker):
    run_container = mocker.patch.object(testing, "run_container", return_value=0)
    assert testing.run_integration() == 0
    run_container.assert_called_once_with("test", ["common"])


def test_run_integration_forwards_role(mocker):
    run_container = mocker.patch.object(testing, "run_container", return_value=0)
    testing.run_integration("jellyfin")
    run_container.assert_called_once_with("test", ["jellyfin"])


def test_run_integration_propagates_return_code(mocker):
    mocker.patch.object(testing, "run_container", return_value=5)
    assert testing.run_integration() == 5
