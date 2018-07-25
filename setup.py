import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

exec(open('plateo/version.py').read()) # loads __version__

setup(name='plateo',
      version=__version__,
      author='Zulko',
    description='Read/write microplate and picklist data for lab automation',
    long_description=open('README.rst').read(),
    license='MIT',
    keywords="microplate biology parser converter report",
    packages= find_packages(exclude='docs'),
    include_package_data=True,
    install_requires= ['pandas>=0.22', 'xlwt', 'xlrd', 'python-box', 'numpy',
                       'matplotlib', 'tqdm', 'pdf_reports', 'flametree',
                       'fuzzywuzzy', 'sequenticon'])
