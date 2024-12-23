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

    mock_drives: bool = CI  # use mock hardware for testing, true in CI

    cmd_timeout: float = 0.5  # command timeout in seconds

    # model parameters
    wheel_diameter: float = 0.32  # wheel diameter in meters
    wheel_accel: float = 1.0  # wheel axle acceleration in m/s^2


class MqttTopics(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="topic_")

    cmd_vc: str = "/motion/cmd_vc"
    status: str = "/motion/status"
