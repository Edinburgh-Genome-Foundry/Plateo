import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

exec(open('plate_converter/version.py').read()) # loads __version__

setup(name='plate_converter',
      version=__version__,
      author='Zulko',
    description='',
    long_description=open('README.rst').read(),
    license='see LICENSE.txt',
    keywords="microplate biology parser converter report",
    packages= find_packages(exclude='docs'),
    install_requires= ['pandas'])
