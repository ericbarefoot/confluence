"""Talk to the Fuji Frenic VFD directly over Modbus, bypassing confluence/MQTT entirely.

For diagnosing whether start_motor()/clear_faults()/send_setpoint()
failing (ok:False, since the recent fix that makes them re-raise on a
comm error instead of silently swallowing it) is a real Modbus/RS-485
problem versus something in confluence's own plumbing. This talks to the
drive directly using the exact same comms settings from
confluence_config.json, with no MQTT/job scheduler involved — if this
also fails, the problem is the physical link (wiring, VFD power, drive
parameters) or the config values, not confluence's code.

Reads each of VFD's poll_* methods individually (each already prints its
own raw exception on failure — see Fuji_VFD_funcs.py — so the actual
Modbus error text, e.g. timeout vs. CRC failure vs. no response, shows up
directly here without anything else in between to obscure it).

Safe: read-only monitoring calls plus poll_status(). Does NOT call
start_motor()/stop_motor()/send_setpoint()/clear_faults() — this is a
communication check, not a motor test.

Usage (from the confluence repo root, on red.lab, inside the venv):
    python scripts/probe_fuji_vfd.py
"""

import json
import sys
from pathlib import Path

# Running this as `python scripts/probe_fuji_vfd.py` puts scripts/ on
# sys.path, not the repo root — so the top-level `Interfaces` package
# (no __init__.py, a namespace package) isn't importable without this.
# confluence_daemon.py doesn't need this since it lives at the repo root
# already.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from Interfaces.Fuji_Frenic_VFD.Fuji_VFD_funcs import VFD

with open("./confluence_config.json", "r") as fid:
    configs = json.load(fid)

comms = configs["Fuji_Frenic_VFD"]["comms"]


def main():
    print(f"Comms settings from confluence_config.json: {comms}")
    vfd = VFD(
        comm_port=comms["com port"],
        server_id=comms["serverID"],
        baudrate=comms["baudrate"],
        bytesize=comms["bytesize"],
        parity=comms["parity"],
        stopbits=comms["stopbits"],
        timeout=comms["timeout"],
    )
    print(f"comm_status: {vfd.comm_status}")
    if vfd.comm == "":
        print("Could not open the serial port at all — check the comm port path"
              " and that nothing else (e.g. a stale confluence process) has it open.")
        return

    print("\n--- poll_state() ---")
    vfd.poll_state()
    print(f"state_message: {getattr(vfd, 'state_message', '<not set>')}")
    print(f"e_stop: {getattr(vfd, 'e_stop', '<not set>')}")

    print("\n--- poll_setpoint() ---")
    vfd.poll_setpoint()
    print(f"setpoint: {getattr(vfd, 'setpoint', '<not set>')}")

    print("\n--- poll_monitoring() ---")
    vfd.poll_monitoring()
    print(f"freq_reference_perc: {getattr(vfd, 'freq_reference_perc', '<not set>')}")
    print(f"output_freq: {getattr(vfd, 'output_freq', '<not set>')}")

    print(f"\ncomm_errors so far: {vfd.comm_errors}")

    print("\n--- poll_status() (full round trip) ---")
    vfd.poll_status()
    print(f"status: {vfd.status}")


if __name__ == "__main__":
    main()
