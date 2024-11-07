#!/usr/bin/env python3
"""

Main machine interface.

inputs:  (velocity, curvature) over mqtt
outputs: setpoints to left and right wheels over CAN

Created on Thu Nov 07 2024

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import asyncio
import time
from roxbot import Node
from roxbot.models.diff_drive import DiffDriveModel

from alpha_motion.config import MachineConfig, MqttTopics
from alpha_motion.utils import Timer


CFG = MachineConfig()
TOPICS = MqttTopics()


class Machine(Node):
    def __init__(self) -> None:
        super().__init__()

        self._cmd_timer = Timer(CFG.cmd_timeout)

        self._log.info(f"Config \n{CFG}")

        self.model = DiffDriveModel(CFG.B, CFG.wheel_diameter, CFG.wheel_accel)

        self._coros.append(self._update_model_loop)
        self._coros.append(self._status_loop)
        self._coros.append(self._send_setpoints)
        self._coros.append(self._on_init)

    async def _on_init(self) -> None:
        """initialize machine"""
        self._log.info("Initializing machine")
        await self.mqtt.register_callback(TOPICS.cmd_vc, self._cmd_callback)

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

        while True:
            dt = time.time() - last_update
            self.model.step(dt)
            last_update = time.time()

            # stop if no new setpoints
            if self._cmd_timer.is_timeout():
                self.model.cmd_lr(0, 0)

            await asyncio.sleep(1 / freq)

    async def _send_setpoints(self, freq: float = 10) -> None:
        """send setpoints to drives"""

        wheel_circumference = CFG.wheel_diameter * 3.14159
        delay = 1 / freq

        while True:
            vl_rps = self.model.vl / wheel_circumference
            vr_rps = self.model.vr / wheel_circumference

            self._log.debug(f"vl={vl_rps:.2f}, vr={vr_rps:.2f}")
            await asyncio.sleep(delay)


async def main() -> None:
    m = Machine()

    await m.main()


if __name__ == "__main__":
    from alpha_motion.runners import run_main

    run_main(main())
