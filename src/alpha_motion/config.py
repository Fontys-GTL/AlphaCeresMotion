#!/usr/bin/env python3
"""
Created on Thu Nov 07 2024

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import os
from typing import Tuple

from pydantic_settings import BaseSettings, SettingsConfigDict

CI = os.getenv("CI", "false").lower() == "true"


class MachineConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="machine_")

    B: float = 1.0  # wheel base

    # left and right wheel
    wheel_ids: Tuple[int, int] = (1, 2)  # odrive axis ids
    wheel_dirs: Tuple[int, int] = (1, -1)  # wheel direction

    can_channel: str = "vcan0"  # can channel name

    mock_drives: bool = CI  # use mock hardware for testing, true in CI

    setpoint_freq: int = 10  # drive setpoint frequency in Hz
