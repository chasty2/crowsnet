"""Tests for the Click CLI dispatch in crowsnet.py."""

import pytest
from click.testing import CliRunner

import crowsnet


@pytest.fixture
def runner():
    return CliRunner()


def test_build_calls_build_container(runner, mocker):
    build = mocker.patch("crowsnet.build_container", return_value=0)
    result = runner.invoke(crowsnet.cli, ["build"])
    assert result.exit_code == 0
    build.assert_called_once_with()


@pytest.mark.parametrize("command", ["deploy", "destroy", "refresh"])
@pytest.mark.parametrize("stack", ["stage", "prod"])
def test_pulumi_commands_pass_stack(runner, mocker, command, stack):
    run = mocker.patch("crowsnet.run_container", return_value=0)
    result = runner.invoke(crowsnet.cli, [command, stack])
    assert result.exit_code == 0
    run.assert_called_once_with(command, [stack])


@pytest.mark.parametrize("command", ["deploy", "destroy", "refresh"])
def test_pulumi_commands_reject_unknown_stack(runner, mocker, command):
    run = mocker.patch("crowsnet.run_container", return_value=0)
    result = runner.invoke(crowsnet.cli, [command, "bogus"])
    assert result.exit_code != 0
    run.assert_not_called()


def test_update_without_limit(runner, mocker):
    run = mocker.patch("crowsnet.run_container", return_value=0)
    result = runner.invoke(crowsnet.cli, ["update"])
    assert result.exit_code == 0
    run.assert_called_once_with("update", None)


def test_update_with_limit(runner, mocker):
    run = mocker.patch("crowsnet.run_container", return_value=0)
    result = runner.invoke(crowsnet.cli, ["update", "--limit", "gate"])
    assert result.exit_code == 0
    run.assert_called_once_with("update", ["--limit", "gate"])


def test_configure_without_options(runner, mocker):
    run = mocker.patch("crowsnet.run_container", return_value=0)
    result = runner.invoke(crowsnet.cli, ["configure"])
    assert result.exit_code == 0
    run.assert_called_once_with("configure", None)


def test_configure_with_all_options(runner, mocker):
    run = mocker.patch("crowsnet.run_container", return_value=0)
    result = runner.invoke(
        crowsnet.cli,
        ["configure", "--tags", "users", "--limit", "gate", "--check"],
    )
    assert result.exit_code == 0
    run.assert_called_once_with(
        "configure", ["--tags", "users", "--limit", "gate", "--check"]
    )


def test_test_runs_pytest_by_default(runner, mocker):
    run_pytest = mocker.patch("crowsnet.run_pytest", return_value=0)
    run_integration = mocker.patch("crowsnet.run_integration", return_value=0)
    result = runner.invoke(crowsnet.cli, ["test"])
    assert result.exit_code == 0
    run_pytest.assert_called_once_with()
    run_integration.assert_not_called()


def test_test_integration_flag_runs_integration(runner, mocker):
    run_pytest = mocker.patch("crowsnet.run_pytest", return_value=0)
    run_integration = mocker.patch("crowsnet.run_integration", return_value=0)
    result = runner.invoke(crowsnet.cli, ["test", "--integration"])
    assert result.exit_code == 0
    run_integration.assert_called_once_with("common")
    run_pytest.assert_not_called()


def test_test_integration_accepts_role(runner, mocker):
    mocker.patch("crowsnet.run_pytest", return_value=0)
    run_integration = mocker.patch("crowsnet.run_integration", return_value=0)
    result = runner.invoke(crowsnet.cli, ["test", "--integration", "--role", "jellyfin"])
    assert result.exit_code == 0
    run_integration.assert_called_once_with("jellyfin")


def test_exit_code_propagates(runner, mocker):
    mocker.patch("crowsnet.run_container", return_value=2)
    result = runner.invoke(crowsnet.cli, ["deploy", "stage"])
    assert result.exit_code == 2
