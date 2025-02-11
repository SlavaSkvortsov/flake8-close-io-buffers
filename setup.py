from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
install_requires = (this_directory / "requirements.txt").read_text().splitlines()

setup(
    name="flake8-close-io-buffers",
    version="0.1.0",
    description="Flake8 plugin to detect opened but not closed IO buffers",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "flake8.extension": [
            "IO100 = flake8_close_io_buffers.plugin:UnclosedIOChecker",
        ],
    },
)
