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


def test_run_integration_builds_container_command(mocker):
    recorder = {}
    mocker.patch.object(testing.subprocess, "run", _fake_run(0, recorder))
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value="secret-token\n")

    assert testing.run_integration() == 0

    cmd = recorder["cmd"]
    assert cmd[0:2] == ["podman", "run"]
    assert "--network" in cmd and "host" in cmd
    assert f"{testing.PROJECT_ROOT}:/workspace" in cmd
    # runs from the role's scenario directory under the mounted repo
    assert "/workspace/ansible/roles/common" in cmd
    # token passed through the environment, not a world-readable mount
    assert "PULUMI_ACCESS_TOKEN=secret-token" in cmd
    # molecule is the entrypoint, given the `test` subcommand
    assert cmd[-4:] == ["--entrypoint", "molecule", testing.CONTAINER_NAME, "test"]


def test_run_integration_accepts_role(mocker):
    recorder = {}
    mocker.patch.object(testing.subprocess, "run", _fake_run(0, recorder))
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value="t")

    testing.run_integration("jellyfin")
    assert "/workspace/ansible/roles/jellyfin" in recorder["cmd"]


def test_run_integration_propagates_return_code(mocker):
    mocker.patch.object(testing.subprocess, "run", _fake_run(5))
    mocker.patch("pathlib.Path.exists", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value="t")
    assert testing.run_integration() == 5