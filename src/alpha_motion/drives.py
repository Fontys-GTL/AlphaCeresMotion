#!/usr/bin/env python3
"""

Wrapper for odrives. Provides a simple interface L anr R wheels.

Created on Thu Nov 07 2024

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging
from odrive_can import ODriveCAN
from odrive_can.mock import ODriveCANMock
from odrive_can.odrive import DriveError, HeartbeatError

from .config import MachineConfig
from .utils import log_call

CFG = MachineConfig()


class Drive:
    """Base class for odrive motors"""

    def __init__(self, axis_id: int, name: str = "drive", direction: int = 1) -> None:
        self.log = logging.getLogger(name)

        self.name = name
        self.odrv: ODriveCAN = ODriveCAN(axis_id=axis_id, interface=CFG.can_channel)

        self.direction = direction
        self.odrv.set_controller_mode("VELOCITY_CONTROL", "VEL_RAMP")

    @log_call()
    async def start(self) -> None:
        """start odrive"""
        await self.odrv.start()
        self.odrv.clear_errors()

    @log_call()
    def stop(self) -> None:
        """stop odrive"""
        self.odrv.stop()

    @log_call()
    async def init(self) -> None:
        """initialize motor"""
        self.clear_errors()
        await self.odrv.wait_for_heartbeat()
        await self.arm()

    @log_call()
    async def calibrate(self) -> None:
        self.odrv.clear_errors()
        await self.odrv.set_axis_state("FULL_CALIBRATION_SEQUENCE")
        self.log.info("Calibration started...")
        while self.odrv.axis_state != "IDLE":
            self.log.info("waiting for IDLE state")
            await asyncio.sleep(1)
        self.log.info("Calibration finished")

    @log_call()
    async def arm(self) -> None:
        """Arms the motor making it ready for input. This only works if all errors have been cleared."""
        await self.odrv.set_axis_state("CLOSED_LOOP_CONTROL")
        self.set_velocity_rps(0)
        self.log.info("Armed")

    @log_call()
    def disarm(self) -> None:
        """Disarms the motor stopping it and ignoring input."""
        self.odrv.set_axis_state_no_wait("IDLE")
        self.set_velocity_rps(0)
        self.log.info("Disarmed")

    @log_call()
    def clear_errors(self) -> None:
        """Clears all active errors"""
        self.odrv.clear_errors()

    def is_error(self) -> bool:
        """Returns True if there are any errors"""
        try:
            self.odrv.check_errors()
        except (DriveError, HeartbeatError):
            return True

        return False

    def set_velocity_rps(
        self,
        vel: float,
    ) -> None:
        """velocity in revolutions per second"""

        self.odrv.set_input_vel(vel * self.direction)


async def mock_drives() -> None:
    """create mock drives"""

    # create mocks
    left_wheel = ODriveCANMock(axis_id=CFG.wheel_ids[0], channel=CFG.can_channel)
    left_wheel.odrive.control_mode = "VELOCITY_CONTROL"
    right_wheel = ODriveCANMock(axis_id=CFG.wheel_ids[1], channel=CFG.can_channel)
    right_wheel.odrive.control_mode = "VELOCITY_CONTROL"

    async with asyncio.TaskGroup() as tg:
        tg.create_task(left_wheel.main())
        tg.create_task(right_wheel.main())
