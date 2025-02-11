from setuptools import setup, find_packages

setup(
    name="flake8-close-io-buffers",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Flake8 plugin to detect opened but not closed IO buffers",
    packages=find_packages(),
    install_requires=[line.strip() for line in open("requirements.txt").read().splitlines() if line.strip()],
    extras_require={
        "dev": [line.strip() for line in open("requirements-dev.txt").read().splitlines() if line.strip()],
    },
    entry_points={
        "flake8.extension": [
            "IO100 = flake8_close_io_buffers.plugin:UnclosedIOChecker",
        ],
    },
)

