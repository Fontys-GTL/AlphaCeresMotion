"""main entry point for alpha_motion."""

from alpha_motion import __version__
from alpha_motion.runners import run_main
import alpha_motion.machine as machine


def main() -> None:
    """main entry point for alpha_motion."""
    print(f"alpha_motion version: {__version__}!")
    run_main(machine.main())


if __name__ == "__main__":
    main()
