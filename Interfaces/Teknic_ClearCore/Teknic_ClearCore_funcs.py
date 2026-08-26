"""Thin wrapper around safl_ocean_hardware's TeknicMotor for confluence.

One physical Teknic ClearCore controller drives the flume's weir gate
elevation axis and also carries the digital IO channels laguna's flow
subsystem uses for the qin/qaux solenoid valves — see
laguna/src/laguna/weir/controller.py and laguna/src/laguna/flow/controller.py
for the client side of this split (weir uses the motion methods below,
flow only ever calls set_io()). Both are exposed here through a single
TeknicMotor connection, matching how the driver and the physical wiring
are actually shared, rather than pretending they are two independent axes.
"""

import datetime

from safl_ocean_hardware.motor import TeknicMotor


class TeknicClearCore:
    def __init__(self, comm_port, baudrate=9600):
        self.motor = TeknicMotor(comm_port, baudrate)
        self.connected = self.motor.connect()
        self.weir_status = {}
        self.valve_status = {"qin_open": False, "qaux_open": False}

    def poll_weir_status(self):
        """Poll the ClearCore and update self.weir_status for publishing.

        Translates the driver's raw poll_status() keys (position,
        VelSetPoint, StepsActive, ...) into the elevation_mm/is_moving
        shape laguna.weir.controller.SaflWeirController expects on its
        status topic.
        """
        raw = self.motor.poll_status()
        self.weir_status = {
            "timestamp": datetime.datetime.now().isoformat(timespec="milliseconds"),
            "elevation_mm": raw.get("position"),
            "is_moving": bool(raw.get("StepsActive")),
            "velocity_setpoint": raw.get("VelSetPoint"),
            "enabled": raw.get("Enabled"),
            "motor_in_fault": raw.get("MotorInFault"),
        }

    def poll_valve_status(self):
        """Update self.valve_status for publishing.

        The ClearCore digital outputs are write-only from this driver (no
        readback), so this just timestamps the last-commanded qin/qaux
        state rather than a live hardware readback.
        """
        self.valve_status["timestamp"] = datetime.datetime.now().isoformat(
            timespec="milliseconds"
        )

    def handle_weir_command(self, command, args):
        """Execute a weir-gate command. Returns a reply dict (without request_id)."""
        if command == "set_position":
            self.motor.set_absolute_position(args["mm"])
            return {"ok": True}
        if command == "move_absolute":
            accepted = self.motor.move_to_position(args["mm"])
            return {"ok": True, "accepted": bool(accepted)}
        if command == "set_velocity":
            self.motor.set_velocity(args["mm_per_sec"])
            return {"ok": True}
        if command == "enable":
            self.motor.enable()
            return {"ok": True}
        if command == "disable":
            self.motor.disable()
            return {"ok": True}
        if command == "stop":
            self.motor.stop()
            return {"ok": True}
        if command == "clear_faults":
            self.motor.clear_faults()
            return {"ok": True}
        if command == "home":
            ok = self.motor.find_home(home_position_mm=args.get("home_offset_mm", 0.0))
            return {"ok": bool(ok)}
        return {"ok": False, "error": f"unknown command {command!r}"}

    def handle_valve_command(self, command, args):
        """Execute a flow-valve command. Returns a reply dict (without request_id)."""
        if command == "set_io":
            self.motor.set_io(args["channel"], args["state"])
            if args["channel"] == 0:
                self.valve_status["qin_open"] = bool(args["state"])
            elif args["channel"] == 1:
                self.valve_status["qaux_open"] = bool(args["state"])
            return {"ok": True}
        return {"ok": False, "error": f"unknown command {command!r}"}
