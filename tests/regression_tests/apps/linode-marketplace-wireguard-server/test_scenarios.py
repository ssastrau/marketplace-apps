from regression_tests.services.wireguard_server.wireguard_server_service import (
    WireGuardServerService,
)


def test_wireguard_server_up_and_listening_on_the_configured_port(remote_exec):
    # Verifies that the unit is active and the kernel is listening on the configured port.
    service = WireGuardServerService(remote_exec)

    state = service.unit_state()
    enabled = service.unit_enabled()
    flags = service.link_flags()
    configured_port = service.config_value("ListenPort")
    listening_port = service.interface_listen_port()

    assert state == "active", f"{WireGuardServerService.UNIT} is not active: {state}"
    assert enabled == "enabled", (
        f"{WireGuardServerService.UNIT} is not enabled, so the server would not survive a reboot: {enabled}"
    )
    assert "UP" in flags, f"wg0 is not up: {flags!r}"
    assert listening_port == configured_port, (
        f"kernel is listening on {listening_port!r} but the config declares {configured_port!r}"
    )
