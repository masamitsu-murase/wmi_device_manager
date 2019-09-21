# Always prefer setuptools over distutils
from setuptools import setup
from os import path
# io.open is needed for projects that support Python 2.7
# It ensures open() defaults to text mode with universal newlines,
# and accepts an argument to specify the text encoding
# Python 3 only projects can skip this import
from io import open

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='wmidevicemanager',
    version='1.2.3',
    description='A library to get information in device manager based on WMI.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/masamitsu-murase/wmi_device_manager',
    author='Masamitsu MURASE',
    author_email='masamitsu.murase@gmail.com',
    license='MIT',
    keywords='WMI device manager',
    packages=['wmidevicemanager'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    install_requires=['comtypes'],
    project_urls={
        'Bug Reports':
        'https://github.com/masamitsu-murase/wmi_device_manager/issues',
        'Source': 'https://github.com/masamitsu-murase/wmi_device_manager',
    },
)
