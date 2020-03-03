from os.path import join, dirname

from setuptools import setup, find_packages

import tagcounter
setup(
    name='tagcounter',
    version=tagcounter.__version__,
    packages=find_packages(),
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    include_package_data=True,
    scripts=["tagcounter/core.py"],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=["PyYAML>=5.1"],

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        "tagcounter": ["*.log", "*.txt", "*.yml", "*.db"],
    },
    test_suite='test'
)