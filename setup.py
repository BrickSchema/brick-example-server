from setuptools import setup, find_packages


def get_long_description():
    return open("README.md", "r", encoding="utf8").read()


def get_requirements():
    with open("requirements.txt") as f:
        return f.read().splitlines()


setup(
    name="brick-server-minimal",
    version="0.0.1",
    keywords=("brick", "brick-server"),
    description="brick server minimal",
    long_description=get_long_description(),
    license="MIT",
    url="https://gitlab.com/mesl/brickserver/brick-server-minimal",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    platforms="any",
    install_requires=get_requirements(),
    scripts=[],
    entry_points={"console_scripts": ["test = test.help:main"]},
)
