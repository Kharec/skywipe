"""Command implementations for Skywipe CLI."""

from skywipe.configuration import Configuration
import sys

def run_configure():
    config = Configuration()
    config.create()
