"""

test drives with odrive mock via vcan
vcan0 needs to be set up on the host machine

"""

import asyncio
from typing import AsyncIterator
from contextlib import asynccontextmanager
import os
import pytest
from odrive_can.mock import ODriveCANMock

from alpha_motion.drives import Drive


# enable tests if vcan0 is available
if not os.path.exists("/sys/class/net/vcan0") or os.environ.get("CI"):
    pytestmark = pytest.mark.skip(reason="No vcan0 present.")


# tried to use a fixture, but it did not work. so using a context manager
@asynccontextmanager
async def odrive_can_context(
    axis_id: int = 1, channel: str = "vcan0"
) -> AsyncIterator[ODriveCANMock]:
    odrv = ODriveCANMock(axis_id=axis_id, channel=channel)
    odrv_task = asyncio.create_task(odrv.main())
    await asyncio.sleep(0.2)  # Allow some time for the mock to initialize
    try:
        yield odrv
    finally:
        odrv_task.cancel()
        try:
            await odrv_task
        except asyncio.CancelledError:
            pass


@pytest.mark.asyncio
async def test_wheel_drive() -> None:
    """Test steering drive with odrive mock."""
    async with odrive_can_context(axis_id=2, channel="vcan0"):
        drive = Drive(2, direction=1, name="wheel_drive")
        await drive.start()
        await drive.init()
        await drive.arm()
        drive.set_velocity_rps(0.5)
        await asyncio.sleep(1.0)
        drive.disarm()
        drive.stop()
