#!/usr/bin/env python3
"""
alpha_motion CLI
"""

import click

from alpha_motion import __version__
from alpha_motion.runners import run_main


@click.group()
@click.version_option(version=__version__)
def cli() -> None:
    pass  # pragma: no cover


@cli.command()
def info() -> None:
    """Print package info"""
    print(__version__)


cli.add_command(info)

# run group


@click.group()
def run() -> None:
    """Run commands"""
    pass


cli.add_command(run)


@run.command()
def mock_drives() -> None:
    """Run mock drives"""
    from alpha_motion.drives import mock_drives

    run_main(mock_drives())


@run.command()
def machine() -> None:
    """Run machine"""
    from alpha_motion.machine import main

    run_main(main(), trace_on_exc=True)


if __name__ == "__main__":
    cli()  # pragma: no cover
