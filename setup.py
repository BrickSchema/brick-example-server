from setuptools import setup, find_packages
from pkg_resources import parse_requirements

__author__ = 'Jason Koh'
__version__ = '0.0.1'

install_reqs = parse_requirements(open('requirements.txt'))
reqs = [ir.name for ir in install_reqs]

setup(
    name = 'brick_server',
    version = __version__,
    packages = find_packages(),
    description = 'Brick server and subpackages',
    install_requires = reqs,
)

