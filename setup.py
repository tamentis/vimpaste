try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

import vimpaste

setup(
    name="vimpaste",
    version=vimpaste.__version__,
    description="Web App for vimpaste.com",
    author="Bertrand Janin",
    author_email="tamentis@neopulsar.org",
    url="http://vimpaste.com/",
    license="LICENSE.txt",
    install_requires=[
        "couchdb>=0.8",
    ],
    packages=find_packages(exclude=['ez_setup']),
    scripts=[
        "tools/serve.py",
    ],
    include_package_data=True,
    test_suite="nose.collector",
)
