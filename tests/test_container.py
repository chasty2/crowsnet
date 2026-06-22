"""Tests for the podman command construction in utilities/container.py."""

from types import SimpleNamespace

from utilities import container


def _fake_run(returncode=0, recorder=None):
    """Build a subprocess.run stand-in that records the command it received."""

    def _run(cmd, *args, **kwargs):
        if recorder is not None:
            recorder["cmd"] = cmd
            recorder["cwd"] = kwargs.get("cwd")
        return SimpleNamespace(returncode=returncode)

    return _run


def test_run_container_builds_expected_command(mocker):
    recorder = {}
    mocker.patch.object(container.subprocess, "run", _fake_run(0, recorder))
    mocker.patch.object(container.sys.stdout, "isatty", return_value=True)

    rc = container.run_container("configure")

    assert rc == 0
    cmd = recorder["cmd"]
    assert cmd[:6] == ["podman", "run", "-it", "--rm", "--userns=keep-id", "--network"]
    assert "host" in cmd
    assert f"{container.ANSIBLE_DIR}:/etc/ansible" in cmd
    assert f"{container.PULUMI_DIR}:/pulumi" in cmd
    assert cmd[-1] == "configure"


def test_run_container_allocates_tty_only_when_attached(mocker):
    recorder = {}
    mocker.patch.object(container.subprocess, "run", _fake_run(0, recorder))
    mocker.patch.object(container.sys.stdout, "isatty", return_value=True)
    container.run_container("configure")
    assert recorder["cmd"][2] == "-it"

    mocker.patch.object(container.sys.stdout, "isatty", return_value=False)
    container.run_container("configure")
    assert recorder["cmd"][2] == "-i"


def test_run_container_appends_args(mocker):
    recorder = {}
    mocker.patch.object(container.subprocess, "run", _fake_run(0, recorder))

    container.run_container("deploy", ["stage"])

    cmd = recorder["cmd"]
    assert cmd[-2:] == ["deploy", "stage"]


def test_run_container_no_args_does_not_append(mocker):
    recorder = {}
    mocker.patch.object(container.subprocess, "run", _fake_run(0, recorder))

    container.run_container("test", None)

    assert recorder["cmd"][-1] == "test"


def test_run_container_returns_return_code(mocker):
    mocker.patch.object(container.subprocess, "run", _fake_run(3))
    assert container.run_container("configure") == 3


def test_build_container_copies_and_cleans_up(mocker):
    recorder = {}
    mocker.patch.object(container.subprocess, "run", _fake_run(0, recorder))
    copy = mocker.patch.object(container.shutil, "copy2")
    unlink = mocker.patch("pathlib.Path.unlink")

    rc = container.build_container()

    assert rc == 0
    # pyproject.toml and uv.lock copied into the docker build context
    assert copy.call_count == 2
    # build runs from the docker dir
    assert recorder["cwd"] == container.DOCKER_DIR
    assert recorder["cmd"][:3] == ["podman", "build", "."]
    # both copied files cleaned up afterward
    assert unlink.call_count == 2


def test_build_container_cleans_up_on_failure(mocker):
    mocker.patch.object(container.shutil, "copy2")
    mocker.patch.object(
        container.subprocess, "run", side_effect=RuntimeError("boom")
    )
    unlink = mocker.patch("pathlib.Path.unlink")

    try:
        container.build_container()
    except RuntimeError:
        pass

    # finally block still removes the copied files
    assert unlink.call_count == 2
