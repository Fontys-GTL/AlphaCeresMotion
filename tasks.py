# type: ignore
import os
import re
import time
from pathlib import Path
import shutil

from click import prompt
from invoke import task


def get_version_from_dist():
    dist_files = os.listdir("dist")
    for filename in dist_files:
        match = re.match(r"beta_main-(\d+\.\d+\.\d+(\.dev\d+)?)", filename)
        if match:
            return match.group(1)
    raise ValueError("Version not found in dist folder")


@task
def clean(ctx):
    """
    Remove all files and directories that are not under version control to ensure a pristine working environment.
    Use caution as this operation cannot be undone and might remove untracked files.

    """

    ctx.run("git clean -nfdx")

    if (
        prompt(
            "Are you sure you want to remove all untracked files? (y/n)", default="n"
        )
        == "y"
    ):
        ctx.run("git clean -fdx")


@task
def lint(ctx):
    """
    Perform static analysis on the source code to check for syntax errors and enforce style consistency.
    """
    ctx.run("pylint -E src tests")
    ctx.run("mypy src")


@task
def test(ctx):
    """
    Run tests with coverage reporting to ensure code functionality and quality.
    """
    ctx.run("pytest --cov=src --cov-report term-missing tests")


@task
def uml(ctx):
    """
    Generate UML diagrams from the source code using pyreverse.
    """
    ctx.run("mkdir -p docs/uml")
    ctx.run("pyreverse src/alpha_motion -o png -d docs/uml")


@task
def ci(ctx):
    """
    run ci locally in a fresh container

    """
    t_start = time.time()
    # get script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        ctx.run(f"docker run --rm -v {script_dir}:/workspace roxauto/python-ci")
    finally:
        t_end = time.time()
        print(f"CI run took {t_end - t_start:.1f} seconds")


@task
def build_package(ctx):
    """
    Build package in docker container.
    """

    ctx.run("rm -rf dist")
    t_start = time.time()
    # get script directory
    script_dir = os.path.dirname(os.path.realpath(__file__))
    try:
        ctx.run(
            f"docker run --rm -v {script_dir}:/workspace roxauto/python-ci /scripts/build.sh"
        )
    finally:
        t_end = time.time()
        print(f"CI run took {t_end - t_start:.1f} seconds")


@task
def build_image(ctx):
    """build docker image locally. run on host machine"""
    # Set the Docker image name
    img = "local/alpha-motion:latest"

    # Print message for building Docker image
    print(f"Building Docker image {img}")

    pkg_path = Path("dist")
    if not pkg_path.exists():
        print("No dist directory found, building package first")
        build_package(ctx)

    tmp_pkg_path = Path("docker/dist")
    if tmp_pkg_path.exists():
        shutil.rmtree(tmp_pkg_path)

    shutil.copytree("dist", "docker/dist")

    # Build the Docker image
    ctx.run(f"docker build --no-cache -t {img} docker")

    # Clean up the copied dist folder
    shutil.rmtree("docker/dist")

    print(f"Built Docker image {img}")
