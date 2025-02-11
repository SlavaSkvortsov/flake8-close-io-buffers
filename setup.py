from setuptools import setup, find_packages

setup(
    name="flake8-close-io-buffers",
    version="0.1.0",
    description="Flake8 plugin to detect opened but not closed IO buffers",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "flake8.extension": [
            "IO100 = flake8_close_io_buffers.plugin:UnclosedIOChecker",
        ],
    },
)
