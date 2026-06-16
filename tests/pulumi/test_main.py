"""Tests for stack -> VM selection in pulumi/vms.py."""

import pytest

import vms


def test_select_stage_returns_stage_vms():
    selected = vms.select_vms("stage")
    assert selected is vms.STAGE_VMS
    assert [v["name"] for v in selected] == ["lab"]


def test_select_prod_returns_prod_vms():
    selected = vms.select_vms("prod")
    assert selected is vms.PROD_VMS
    assert [v["name"] for v in selected] == ["gate", "proxy", "bailey", "kube-1"]


def test_select_unknown_stack_raises():
    with pytest.raises(ValueError, match="Unknown stack"):
        vms.select_vms("bogus")
