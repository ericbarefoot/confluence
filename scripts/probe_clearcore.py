"""Identify which remaining hub port is the Teknic ClearCore.

For use after probe_serial_ports.py has already ruled out Massa_Ultrasonic
and Fuji_Frenic_VFD — this checks whatever's left using the real
safl_ocean_hardware driver. Safe: connect() + poll_status() only, no
motion commands (move_to_position/find_home aren't called here).

Usage (from the confluence repo root, inside the venv):
    python scripts/probe_clearcore.py /dev/serial/by-id/foo /dev/serial/by-id/bar ...
"""

import sys

from safl_ocean_hardware.motor import TeknicMotor

BAUDRATE = 9600  # matches confluence_config.json's Teknic_ClearCore.comms.baudrate


def probe(port: str) -> None:
    print(f"{port}:")
    motor = TeknicMotor(port, BAUDRATE)
    try:
        if not motor.connect():
            print("  -> no response")
            return
        status = motor.poll_status()
        print(f"  -> connected, status: {status}")
    except Exception as e:
        print(f"  -> error: {e}")
    finally:
        motor.disconnect()


def main():
    ports = sys.argv[1:]
    if not ports:
        print("Usage: python scripts/probe_clearcore.py <port> [<port> ...]")
        sys.exit(1)
    for port in ports:
        probe(port)


if __name__ == "__main__":
    main()
