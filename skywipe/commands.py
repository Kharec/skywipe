"""Command implementations for Skywipe CLI."""

from skywipe.configuration import Configuration


def run_configure():
    config = Configuration()
    config.create()
