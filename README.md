# AlphaCeresMotion



Motion container for Alpha Ceres machine



## Development


1. develop and test in devcontainer (VSCode)
2. trigger ci builds by bumping version with a tag. (see `.gitlab-ci.yml`)

## Tooling

* Automation: `invoke` - run `invoke -l` to list available commands. (uses `tasks.py`)
* Verisoning : `setuptools_scm`
* Linting and formatting : `ruff`
* Typechecking: `mypy`

## What goes where
* `src/alpha_motion` app code. `pip install .` .
* `tasks.py` automation tasks.

## How to run integration
To do some integration testing, this container depends on a MQTT broker. We can run this by `docker compose up` in the integration folder. This will start a mosquitto container that acts as an MQTT broker. This has to be run on the host system.
##How to run integration
To do some integration testing, this container depends on a MQTT broker. We can run this by `docker compose up` in the integration folder. This will start a mosquitto container that acts as an MQTT broker. This has to be run on the host system.
The machine can be tested with motion_tester. It will publish with a velocity of 0.5 and a varying curvature between -1 and 1.
You can visualise the sent MQTT messages with `mosquitto_sub -t /# -v`. This will print all published MQTT messages.

