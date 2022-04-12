from setuptools import setup, find_packages


setup(
    name='binding',
    version='0.0.1',
    packages=find_packages(include=['pyC', 'pyC.*']),
    install_requires=[
        "pycparser",
    ]
)
