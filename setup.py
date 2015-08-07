#!/usr/bin/env python
import os
import setuptools

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
VERSION_FILE = os.path.join(BASE_DIR, "cutiestix", 'version.py')
README_FILE  = os.path.join(BASE_DIR, "README.rst")


def normalize(version):
    return version.split()[-1].strip("\"'")


def get_version():
    with open(VERSION_FILE) as f:
        version = next((line for line in f if line.startswith("__version__")))
        return normalize(version)


with open(README_FILE) as f:
    readme = f.read()


install_requires = [
    # PyQt >= 4.8, < 5.0
    'stix-validator>=2.4.0'
]

extras_require = {
    'docs': [],
    'test': [
        "nose==1.3.0",
        "tox==1.6.1"
    ],
}

setuptools.setup(
    name='cutiestix',
    description='A desktop application interface to stix-validator',
    author='Bryan Worrell',
    author_email='',
    url='https://github.com/bworrell',
    version=get_version(),
    packages=setuptools.find_packages(),
    scripts=['scripts/run-cutiestix.py'],
    include_package_data=True,
    install_requires=install_requires,
    extras_require=extras_require,
    long_description=readme,
    keywords="STIX stix-validator Qt desktop"
)
