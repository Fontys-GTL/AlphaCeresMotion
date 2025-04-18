#!/usr/bin/env python3
"""

Main machine interface.

inputs:  (velocity, curvature) over mqtt
outputs: setpoints to left and right wheels over CAN

Created on Thu Nov 07 2024

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import asyncio
import os
import time

from odrive_can.odrive import CanMsg, ODriveCAN
from odrive_can.tools import UDP_Client
from roxbot import Node
from roxbot.models.diff_drive import DiffDriveModel

from alpha_motion.config import MachineConfig, MqttTopics
from alpha_motion.drives import Drive
from alpha_motion.utils import Timer

CFG = MachineConfig()
TOPICS = MqttTopics()


udp_client = UDP_Client(
    host=os.getenv("UDP_DATA_DEST", "localhost")
)  # udp client for sending data to plotjuggler


def feedback_callback(msg: CanMsg, caller: ODriveCAN) -> None:
    """Position callback, send data as MQTT message"""
    data = msg.data
    data["setpoint"] = caller.setpoint
    data["ts"] = time.time()

    data = {
        "pos": round(data["Pos_Estimate"], 3),
        "vel": round(data["Vel_Estimate"], 3),
        "sp": round(data["setpoint"], 3),
        "ts": round(data["ts"], 3),
    }

    msg_out = {f"axis_id_{caller.axis_id}": data}

    udp_client.send(msg_out, add_timestamp=False)


class Machine(Node):
    def __init__(self) -> None:
        super().__init__()

        self._cmd_timer = Timer(CFG.cmd_timeout)

        self._log.info(f"Config \n{CFG}")

        self.model = DiffDriveModel(CFG.B, CFG.wheel_diameter, CFG.wheel_accel)

        self.left_wheel = Drive(CFG.wheel_ids[0], "left_wheel", CFG.wheel_dirs[0])
        self.left_wheel.odrv.feedback_callback = feedback_callback

        self.right_wheel = Drive(CFG.wheel_ids[1], "right_wheel", CFG.wheel_dirs[1])
        self.right_wheel.odrv.feedback_callback = feedback_callback

        self.drives = [self.left_wheel, self.right_wheel]

        self._coros.append(self._update_model_loop)
        self._coros.append(self._status_loop)
        self._coros.append(self._send_setpoints)
        self._coros.append(self.check_drives_alive)

    async def _on_init(self) -> None:
        """initialize machine"""
        self._log.info("Initializing machine")
        await self.mqtt.register_callback(TOPICS.cmd_vc, self._cmd_callback)

        for drv in self.drives:
            await drv.start()
            await drv.init()

    async def check_drives_alive(self) -> None:
        """check if drives are alive, raise exception if not"""

        await asyncio.sleep(3)  # wait for drives to start

        while True:
            for drv in self.drives:
                drv.odrv.check_alive()  # will raise exception if not alive
                drv.odrv.check_errors()  # will raise exception if errors
            await asyncio.sleep(1)

    def _cmd_callback(self, msg: list | dict) -> None:
        """callback for motion commands"""
        self._log.debug(f"cmd callback {msg}")

        try:
            assert isinstance(msg, dict)
            v_linear = msg["v_linear"]
            curvature = msg["curvature"]
            self.model.cmd_curvature(v_linear, curvature)

            self._cmd_timer.reset()
        except Exception as e:
            self._log.error(f"Invalid message {msg}: {e}")

    async def _status_loop(self) -> None:
        counter = 0

        while True:
            await self.mqtt.publish(TOPICS.status, f"Heartbeat {counter}")
            counter += 1
            await asyncio.sleep(1)

    async def _update_model_loop(self, freq: float = 100) -> None:
        """update setpoints for driving and steering wheels"""

        self._log.info("Starting model update loop")
        last_update = time.time()

        timeout_warned = False

        while True:
            dt = time.time() - last_update
            self.model.step(dt)
            last_update = time.time()

            # stop if no new setpoints
            if self._cmd_timer.is_timeout():
                if not timeout_warned:
                    self._log.warning("Setpoint timeout, stopping.")
                    timeout_warned = True
                self.model.cmd_lr(0, 0)
            else:
                if timeout_warned:
                    self._log.info("Setpoints resumed.")
                timeout_warned = False

            await asyncio.sleep(1 / freq)

    async def _send_setpoints(self, freq: float = 10.0) -> None:
        """send setpoints to drives"""

        wheel_circumference = CFG.wheel_diameter * 3.14159
        delay = 1 / freq

        while True:
            vl_rps = self.model.vl / wheel_circumference
            vr_rps = self.model.vr / wheel_circumference

            self._log.debug(f"vl={vl_rps:.2f}, vr={vr_rps:.2f}")

            udp_client.send({"setpoints": {"vl": vl_rps, "vr": vr_rps}})

            self.left_wheel.set_velocity_rps(vl_rps)
            self.right_wheel.set_velocity_rps(vr_rps)

            await asyncio.sleep(delay)


async def main() -> None:
    machine = Machine()

    await machine.main()


if __name__ == "__main__":
    from alpha_motion.runners import run_main

    run_main(main(), trace_on_exc=True)
