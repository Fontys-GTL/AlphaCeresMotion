#!/usr/bin/env python3
"""
send test motion commands

Created on Thu Nov 07 2024

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import asyncio
from roxbot import Node
from alpha_motion.config import MqttTopics
from alpha_motion.runners import run_main

TOPICS = MqttTopics()


class MotionTester(Node):
    def __init__(self) -> None:
        super().__init__()

        self._coros.append(self._send_test_cmds)

    async def _send_test_cmds(self) -> None:
        v_linear = 0.5
        curvature = -1.0
        while True:
            msg = {"v_linear": v_linear, "curvature": curvature}
            await self.mqtt.publish(TOPICS.cmd_vc, msg)
            await asyncio.sleep(1)
            curvature += 0.1
            if curvature > 1.0:
                curvature = -1.0


if __name__ == "__main__":
    tester = MotionTester()
    run_main(tester.main())