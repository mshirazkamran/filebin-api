from importlib.metadata import entry_points
from setuptools import find_packages, setup

setup(
    name = "filebin-cli",
    version = "0.1",
    packages = find_packages(),
    install_requires = [
        "click",
        "requests"
    ],
    entry_points = {
        "console_scripts": [
            'fbin = filebin.main:main',  # 'command = module:function'
        ],
    },
    author = "https://github.com/mshirazkamran",
    description = "A cli tool to temporarily share file wihout any hassle. Uses filebin.net public api"
)