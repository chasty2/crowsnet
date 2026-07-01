"""Tests for the ProxmoxVM component in pulumi/components.py."""

import pulumi


class _Mocks(pulumi.runtime.Mocks):
    def new_resource(self, args: pulumi.runtime.MockResourceArgs):
        return [args.name + "_id", args.inputs]

    def call(self, args: pulumi.runtime.MockCallArgs):
        return {}


pulumi.runtime.set_mocks(_Mocks())

from components import ProxmoxVM  # noqa: E402  (must follow set_mocks)


def _make(template="small", **overrides):
    kwargs = dict(
        name="lab",
        vmid=200,
        cpu=2,
        ram=4096,
        ip="192.168.4.200",
        mac="CA:9B:F1:85:90:C0",
        clone=True,
        template=template,
    )
    kwargs.update(overrides)
    return ProxmoxVM(**kwargs)


@pulumi.runtime.test
def test_small_template_disk_and_clone_source():
    vm = _make(template="small")

    def check(args):
        disks, clone = args
        assert disks[0]["size"] == 36
        assert clone["vm_id"] == 301

    return pulumi.Output.all(vm.vm.disks, vm.vm.clone).apply(check)


@pulumi.runtime.test
def test_large_template_disk_and_clone_source():
    vm = _make(template="large")

    def check(args):
        disks, clone = args
        assert disks[0]["size"] == 130
        assert clone["vm_id"] == 302

    return pulumi.Output.all(vm.vm.disks, vm.vm.clone).apply(check)


@pulumi.runtime.test
def test_clone_flag_controls_full_clone():
    vm = _make(clone=False)

    def check(clone):
        assert clone["full"] is False

    return vm.vm.clone.apply(check)


@pulumi.runtime.test
def test_scalar_inputs_propagate():
    vm = _make(cpu=4, ram=8192, vmid=126, mac="BC:24:11:91:7B:19")

    def check(args):
        cpu, memory, vm_id, networks = args
        assert cpu["cores"] == 4
        assert cpu["type"] == "host"
        assert memory["dedicated"] == 8192
        assert vm_id == 126
        assert networks[0]["mac_address"] == "BC:24:11:91:7B:19"

    return pulumi.Output.all(
        vm.vm.cpu, vm.vm.memory, vm.vm.vm_id, vm.vm.network_devices
    ).apply(check)


@pulumi.runtime.test
def test_ip_address_configured_with_cidr():
    vm = _make(ip="192.168.4.200")

    def check(initialization):
        ipv4 = initialization["ip_configs"][0]["ipv4"]
        assert ipv4["address"] == "192.168.4.200/22"
        assert ipv4["gateway"] == "192.168.4.1"

    return vm.vm.initialization.apply(check)
