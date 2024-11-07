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

from alpha_motion.config import MachineConfig
from alpha_motion.utils import Timer


CFG = MachineConfig()


class Machine(Node):
    def __init__(self) -> None:
        super().__init__()

        self._cmd_timer = Timer(CFG.cmd_timeout)

        self._log.info(f"Config \n{CFG}")

        self.model = DiffDriveModel(CFG.B, CFG.wheel_diameter, CFG.wheel_accel)

        self._coros.append(self._update_model_loop)

    def cmd_curvature(self, v_linear: float, curvature: float) -> None:
        """set velocity and curvature"""
        self.model.cmd_curvature(v_linear, curvature)

    async def _update_model_loop(self, freq: float = 100) -> None:
        """update setpoints for driving and steering wheels"""

        last_update = time.time()

        while True:
            print(".", end="", flush=True)
            dt = time.time() - last_update
            self.model.step(dt)
            last_update = time.time()

            # stop if no new setpoints
            if self._cmd_timer.is_timeout():
                self.model.cmd_lr(0, 0)

            await asyncio.sleep(1 / freq)


# ---------------- test functions ----------------


async def test_machine() -> None:
    m = Machine()

    await m.main()


if __name__ == "__main__":
    from alpha_motion.runners import run_main

    run_main(test_machine())
