from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
install_requires = (this_directory / "requirements.txt").read_text().splitlines()


def get_readme() -> str:
    """read the contents of the README file"""
    with open('README.md', encoding='utf-8') as f:
        return f.read()


setup(
    name="flake8-close-io-buffers",
    version="0.1.3",
    description="Flake8 plugin to detect opened but not closed IO buffers",
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        "flake8.extension": [
            "IO100 = flake8_close_io_buffers.plugin:UnclosedIOChecker",
        ],
    },
    long_description=get_readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/SlavaSkvortsov/flake8-close-io-buffers',
    zip_safe=True,
    classifiers=[
        'Intended Audience :: Developers',

        'Development Status :: 3 - Alpha',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
