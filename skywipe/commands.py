"""Command implementations for Skywipe CLI."""

from skywipe.configure import Configuration


def run_configure():
    config = Configuration()
    config.create()
